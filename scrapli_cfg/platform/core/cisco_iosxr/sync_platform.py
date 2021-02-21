"""scrapli_cfg.platform.core.cisco_iosxr.sync_platform"""
from typing import Any, Callable, List, Optional

from scrapli.driver import NetworkDriver
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.exceptions import DiffConfigError, LoadConfigError
from scrapli_cfg.platform.base.sync_platform import ScrapliCfg
from scrapli_cfg.platform.core.cisco_iosxr.base_platform import CONFIG_SOURCES, ScrapliCfgIOSXRBase
from scrapli_cfg.response import ScrapliCfgResponse


def iosxr_on_open(cls: ScrapliCfg) -> None:
    """
    Scrapli CFG IOSXR On open

    Disable console logging, perhaps more things in the future!

    Args:
        cls: ScrapliCfg object

    Returns:
        None

    Raises:
        N/A

    """
    cls.conn.send_configs(configs=["no logging console", "commit"])


class ScrapliCfgIOSXR(ScrapliCfg, ScrapliCfgIOSXRBase):
    def __init__(
        self,
        conn: NetworkDriver,
        config_sources: Optional[List[str]] = None,
        on_open: Optional[Callable[..., Any]] = None,
    ) -> None:
        if config_sources is None:
            config_sources = CONFIG_SOURCES

        if on_open is None:
            on_open = iosxr_on_open

        super().__init__(conn=conn, config_sources=config_sources, on_open=on_open)

        self._replace = False

        self._in_configuration_session = False
        self._config_privilege_level = "configuration"

    def get_config(self, source: str = "running") -> ScrapliCfgResponse:
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

        if not self._in_configuration_session:
            config_result = self.conn.send_command(command="show running-config")
        else:
            config_result = self.conn.send_config(
                config="show running-config", privilege_level=self._config_privilege_level
            )

        return self._post_get_config(
            response=response,
            source=source,
            scrapli_responses=[config_result],
            result=config_result.result,
        )

    def load_config(self, config: str, replace: bool = False, **kwargs: Any) -> ScrapliCfgResponse:
        """
        Load configuration to a device

        Supported kwargs:
            exclusive: True/False use `configure exclusive` mode

        Args:
            config: string of the configuration to load
            replace: replace the configuration or not, if false configuration will be loaded as a
                merge operation
            kwargs: additional kwargs that the implementing classes may need for their platform

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """
        scrapli_responses = []
        response = self._pre_load_config(config=config)

        exclusive = kwargs.get("exclusive", False)

        config, eager_config = self._prepare_load_config_session_and_payload(
            config=config, replace=replace, exclusive=exclusive
        )

        try:
            config_result = self.conn.send_config(
                config=config, privilege_level=self._config_privilege_level
            )
            scrapli_responses.append(config_result)
            if config_result.failed:
                raise LoadConfigError("failed to load the candidate config into the config session")

            # eager cuz banners and such; perhaps if no banner/macro we can disable eager though....
            if eager_config:
                eager_config_result = self.conn.send_config(
                    config=eager_config, privilege_level=self._config_privilege_level, eager=True
                )
                scrapli_responses.append(eager_config_result)
                if eager_config_result.failed:
                    raise LoadConfigError(
                        "failed to load the candidate config into the config session"
                    )

        except LoadConfigError:
            pass

        return self._post_load_config(
            response=response,
            scrapli_responses=scrapli_responses,
        )

    def abort_config(self) -> ScrapliCfgResponse:
        """
        Abort a configuration -- discards any loaded config

        Args:
            N/A

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """
        response = self._pre_abort_config(session_or_config_file=self._in_configuration_session)

        self.conn._abort_config()  # pylint: disable=W0212
        self._reset_config_session()

        return self._post_abort_config(response=response, scrapli_responses=[])

    def commit_config(self, source: str = "running") -> ScrapliCfgResponse:
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
            source=source, session_or_config_file=self._in_configuration_session
        )

        commit_result = self.conn.send_config(config="commit")
        self._reset_config_session()

        return self._post_commit_config(response=response, scrapli_responses=[commit_result])

    def diff_config(self, source: str = "running") -> ScrapliCfgDiffResponse:
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
            source=source, session_or_config_file=self._in_configuration_session
        )

        try:
            diff_result = self.conn.send_config(
                config=self._get_diff_command(), privilege_level=self._config_privilege_level
            )
            scrapli_responses.append(diff_response)
            if diff_result.failed:
                raise DiffConfigError("failed generating diff for config session")

            source_config_result = self.get_config(source=source)
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
