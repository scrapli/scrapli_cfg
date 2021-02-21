"""scrapli_cfg.platform.core.arista_eos.async_platform"""
from typing import Any, Callable, List, Optional

from scrapli.driver import AsyncNetworkDriver
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.exceptions import DiffConfigError, LoadConfigError
from scrapli_cfg.platform.base.async_platform import AsyncScrapliCfg
from scrapli_cfg.platform.core.arista_eos.base_platform import CONFIG_SOURCES, ScrapliCfgEOSBase
from scrapli_cfg.response import ScrapliCfgResponse


async def async_eos_on_open(cls: AsyncScrapliCfg) -> None:
    """
    Scrapli CFG EOS On open

    Disable console logging, perhaps more things in the future!

    Args:
        cls: ScrapliCfg object

    Returns:
        None

    Raises:
        N/A

    """
    await cls.conn.send_config(config="no logging console")


class AsyncScrapliCfgEOS(AsyncScrapliCfg, ScrapliCfgEOSBase):
    def __init__(
        self,
        conn: AsyncNetworkDriver,
        config_sources: Optional[List[str]] = None,
        on_open: Optional[Callable[..., Any]] = None,
    ) -> None:
        if config_sources is None:
            config_sources = CONFIG_SOURCES

        if on_open is None:
            on_open = async_eos_on_open

        super().__init__(conn=conn, config_sources=config_sources, on_open=on_open)

        self.config_session_name = ""

    async def get_config(self, source: str = "running") -> ScrapliCfgResponse:
        """
        Get device configuration

        Args:
            source: name of the config source, generally running|startup

        Returns:
            ScrapliCfgResponse: response object containing string of the target config source as the
                `result` attribute

        Raises:
            N/A

        """
        response = self._pre_get_config(source=source)

        config_result = await self.conn.send_command(
            command=self._get_config_command(source=source)
        )

        return self._post_get_config(
            response=response,
            source=source,
            scrapli_responses=[config_result],
            result=config_result.result,
        )

    async def load_config(
        self, config: str, replace: bool = False, **kwargs: Any
    ) -> ScrapliCfgResponse:
        """
        Load configuration to a device

        Supported kwargs:
            N/A

        Args:
            config: string of the configuration to load
            replace: replace the configuration or not, if false configuration will be loaded as a
                merge operation
            kwargs: additional kwargs that the implementing classes may need for their platform

        Returns:
            ScrapliCfgResponse: response object;  result will be nothing, but contains the scrapli
                responses from the "load_config" operation

        Raises:
            N/A

        """
        scrapli_responses = []
        response = self._pre_load_config(config=config)
        (
            config,
            eager_config,
            register_config_session,
        ) = self._prepare_load_config_session_and_payload(config=config)

        try:
            if register_config_session:
                # only need to register a session if we havent -- we will reset session to an empty
                # string after any commits/aborts so we know if we are doing "new" operations
                self.conn.register_configuration_session(session_name=self.config_session_name)

            if replace:
                # default the config session - we only need to do this if we are doing a REPLACE
                rollback_clean_config_result = await self.conn.send_config(
                    config="rollback clean-config", privilege_level=self.config_session_name
                )
                if rollback_clean_config_result.failed:
                    raise LoadConfigError("failed to load clean config in configuration session")

            config_result = await self.conn.send_config(
                config=config, privilege_level=self.config_session_name
            )
            scrapli_responses.append(config_result)
            if config_result.failed:
                raise LoadConfigError("failed to load the candidate config into the config session")

            # eager cuz banners and such; perhaps if no banner/macro we can disable eager though....
            if eager_config:
                eager_config_result = await self.conn.send_config(
                    config=eager_config, privilege_level=self.config_session_name, eager=True
                )
                scrapli_responses.append(eager_config_result)
                if eager_config_result.failed:
                    raise LoadConfigError(
                        "failed to load the candidate config into the config session"
                    )

        except LoadConfigError:
            # we catch our own exception so we dont need to do any if failed checks along the way
            # as soon as we hit this (or when we are done w/ the try block) we are done loading the
            # config and can build and return a response object
            pass

        return self._post_load_config(
            response=response,
            scrapli_responses=scrapli_responses,
        )

    async def abort_config(self) -> ScrapliCfgResponse:
        """
        Abort a configuration -- discards any loaded config

        Args:
            N/A

        Returns:
            ScrapliCfgResponse: response object for the abort operation

        Raises:
            N/A

        """
        response = self._pre_abort_config(session_or_config_file=bool(self.config_session_name))

        await self.conn.acquire_priv(desired_priv=self.config_session_name)
        await self.conn._abort_config()  # pylint: disable=W0212
        self._reset_config_session()

        return self._post_abort_config(
            response=response,
            scrapli_responses=[],
        )

    async def commit_config(self, source: str = "running") -> ScrapliCfgResponse:
        """
        Commit a loaded configuration

        Args:
            source: name of the config source to commit against, generally running|startup

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """
        response = self._pre_commit_config(
            source=source, session_or_config_file=bool(self.config_session_name)
        )

        commit_result = await self.conn.send_command(
            command=f"configure session {self.config_session_name} commit"
        )
        self._reset_config_session()

        return self._post_commit_config(response=response, scrapli_responses=[commit_result])

    async def diff_config(self, source: str = "running") -> ScrapliCfgDiffResponse:
        """
        Diff a loaded configuration against the source config store

        Args:
            source: name of the config source to diff against, generally running|startup -- device
                diffs will generally not care about this argument, but the built in scrapli differ
                will

        Returns:
            ScrapliCfgDiffResponse: scrapli cfg diff object

        Raises:
            N/A

        """
        scrapli_responses = []
        device_diff = ""
        source_config = ""

        diff_response = self._pre_diff_config(
            source=source, session_or_config_file=bool(self.config_session_name)
        )

        try:
            diff_result = await self.conn.send_config(
                config="show session-config diffs", privilege_level=self.config_session_name
            )
            scrapli_responses.append(diff_response)
            if diff_result.failed:
                raise DiffConfigError("failed generating diff for config session")

            source_config_result = await self.get_config(source=source)
            source_config = source_config_result.result
            if source_config_result.scrapli_responses:
                scrapli_responses.extend(source_config_result.scrapli_responses)
            if source_config_result.failed:
                raise DiffConfigError("failed fetching source config for diff comparison")

        except DiffConfigError:
            pass

        source_config, candidate_config = self._normalize_source_candidate_configs(
            source_config=source_config
        )

        return self._post_diff_config(
            diff_response=diff_response,
            scrapli_responses=scrapli_responses,
            source_config=source_config,
            candidate_config=candidate_config,
            device_diff=device_diff,
        )
