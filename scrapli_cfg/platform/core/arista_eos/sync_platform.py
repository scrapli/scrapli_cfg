"""scrapli_cfg.platform.core.arista_eos.sync"""

from typing import Any, Callable, List, Optional

from scrapli.driver.core import EOSDriver
from scrapli.response import MultiResponse, Response
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.exceptions import DiffConfigError, LoadConfigError, ScrapliCfgException
from scrapli_cfg.platform.base.sync_platform import ScrapliCfgPlatform
from scrapli_cfg.platform.core.arista_eos.base_platform import CONFIG_SOURCES, ScrapliCfgEOSBase
from scrapli_cfg.response import ScrapliCfgResponse


class ScrapliCfgEOS(ScrapliCfgPlatform, ScrapliCfgEOSBase):
    def __init__(
        self,
        conn: EOSDriver,
        *,
        config_sources: Optional[List[str]] = None,
        on_prepare: Optional[Callable[..., Any]] = None,
        dedicated_connection: bool = False,
        ignore_version: bool = False,
    ) -> None:
        if config_sources is None:
            config_sources = CONFIG_SOURCES

        super().__init__(
            conn=conn,
            config_sources=config_sources,
            on_prepare=on_prepare,
            dedicated_connection=dedicated_connection,
            ignore_version=ignore_version,
        )

        self.conn: EOSDriver

        self.config_session_name = ""

    def _clear_config_session(self, session_name: str) -> Response:
        """
        Clear a configuration session

        Args:
            session_name: name of session to clear

        Returns:
            Response: scrapli response from clearing the session

        Raises:
            N/A

        """
        # Note, early versions of eos supporting config sessions cant be aborted like this, but
        # i dont want to register a config session for each session we want to delete so we'll just
        # roll w/ this for now
        return self.conn.send_command(command=f"configure session {session_name} abort")

    def clear_config_sessions(
        self, session_name: str = "", session_prefix: str = ""
    ) -> ScrapliCfgResponse:
        """
        Clear a specific config session or all sessions with a prefix (ex: scrapli_cfg_)

        Args:
            session_name: name of specific config session to clear
            session_prefix: prefix of session(s) to clear -- ignored if session_name is provided

        Returns:
            ScrapliCfgResponse: response object containing string of the target config source as the
                `result` attribute

        Raises:
            N/A

        """
        scrapli_responses = []
        response = self._pre_clear_config_sessions()

        try:
            get_config_sessions_result = self.conn.send_command(
                command="show config sessions | json"
            )
            scrapli_responses.append(get_config_sessions_result)
            if get_config_sessions_result.failed:
                msg = "failed to show current config sessions"
                self.logger.critical(msg)
                raise ScrapliCfgException(msg)

            config_session_names = self._parse_config_sessions(
                device_output=get_config_sessions_result.result
            )
            for config_session in config_session_names:
                if session_name:
                    if config_session == session_name:
                        clear_config_session_result = self._clear_config_session(
                            session_name=session_name
                        )
                        scrapli_responses.append(clear_config_session_result)
                else:
                    if config_session.startswith(session_prefix):
                        clear_config_session_result = self._clear_config_session(
                            session_name=session_name
                        )
                        scrapli_responses.append(clear_config_session_result)

        except ScrapliCfgException:
            pass

        return self._post_clear_config_sessions(
            response=response, scrapli_responses=scrapli_responses
        )

    def get_version(self) -> ScrapliCfgResponse:
        response = self._pre_get_version()

        version_result = self.conn.send_command(command="show version | i Software image version")

        return self._post_get_version(
            response=response,
            scrapli_responses=[version_result],
            result=self._parse_version(device_output=version_result.result),
        )

    def get_config(self, source: str = "running") -> ScrapliCfgResponse:
        response = self._pre_get_config(source=source)

        config_result = self.conn.send_command(command=self._get_config_command(source=source))

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
            N/A

        Args:
            config: string of the configuration to load
            replace: replace the configuration or not, if false configuration will be loaded as a
                merge operation
            kwargs: additional kwargs that the implementing classes may need for their platform,
                see above for eos supported kwargs

        Returns:
            ScrapliCfgResponse: response object

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

        if register_config_session is True:
            # only need to register a session if we havent -- we will reset session to an empty
            # string after any commits/aborts so we know if we are doing "new" operations
            self.conn.register_configuration_session(session_name=self.config_session_name)

        try:
            if replace:
                # default the config session - we only need to do this if we are doing a REPLACE
                rollback_clean_config_result = self.conn.send_config(
                    config="rollback clean-config", privilege_level=self.config_session_name
                )
                scrapli_responses.append(rollback_clean_config_result)
                if rollback_clean_config_result.failed:
                    msg = "failed to load clean config in configuration session"
                    self.logger.critical(msg)
                    raise LoadConfigError(msg)

            config_result = self.conn.send_config(
                config=config, privilege_level=self.config_session_name
            )
            scrapli_responses.append(config_result)
            if config_result.failed:
                msg = "failed to load the candidate config into the config session"
                self.logger.critical(msg)
                raise LoadConfigError(msg)

            # eager cuz banners and such; perhaps if no banner/macro we can disable eager though....
            if eager_config:
                eager_config_result = self.conn.send_config(
                    config=eager_config, privilege_level=self.config_session_name, eager=True
                )
                scrapli_responses.append(eager_config_result)
                if eager_config_result.failed:
                    msg = "failed to load the candidate config into the config session"
                    self.logger.critical(msg)
                    raise LoadConfigError(msg)

        except LoadConfigError:
            # we catch our own exception so we dont need to do any if failed checks along the way
            # as soon as we hit this (or when we are done w/ the try block) we are done loading the
            # config and can build and return a response object
            pass

        return self._post_load_config(
            response=response,
            scrapli_responses=scrapli_responses,
        )

    def abort_config(self) -> ScrapliCfgResponse:
        response = self._pre_abort_config(session_or_config_file=bool(self.config_session_name))

        self.conn.acquire_priv(desired_priv=self.config_session_name)
        self.conn._abort_config()  # pylint: disable=W0212
        self._reset_config_session()

        return self._post_abort_config(response=response, scrapli_responses=[])

    def commit_config(self, source: str = "running") -> ScrapliCfgResponse:
        response = self._pre_commit_config(
            source=source, session_or_config_file=bool(self.config_session_name)
        )

        commit_results = self.conn.send_commands(
            commands=[
                f"configure session {self.config_session_name} commit",
                "copy running-config startup-config",
            ]
        )
        self._reset_config_session()

        return self._post_commit_config(response=response, scrapli_responses=[commit_results])

    def diff_config(self, source: str = "running") -> ScrapliCfgDiffResponse:
        scrapli_responses = []
        device_diff = ""
        source_config = ""

        diff_response = self._pre_diff_config(
            source=source, session_or_config_file=bool(self.config_session_name)
        )

        try:
            diff_result = self.conn.send_config(
                config="show session-config diffs", privilege_level=self.config_session_name
            )
            scrapli_responses.append(diff_result)
            if diff_result.failed:
                msg = "failed generating diff for config session"
                self.logger.critical(msg)
                raise DiffConfigError(msg)

            device_diff = diff_result.result

            source_config_result = self.get_config(source=source)
            source_config = source_config_result.result

            if isinstance(source_config_result.scrapli_responses, MultiResponse):
                # in this case this will always be a multiresponse or nothing (failure) but mypy
                # doesnt know that, hence the isinstance check
                scrapli_responses.extend(source_config_result.scrapli_responses)

            if source_config_result.failed:
                msg = "failed fetching source config for diff comparison"
                self.logger.critical(msg)
                raise DiffConfigError(msg)

        except DiffConfigError:
            pass

        return self._post_diff_config(
            diff_response=diff_response,
            scrapli_responses=scrapli_responses,
            source_config=self.clean_config(source_config),
            candidate_config=self.clean_config(self.candidate_config),
            device_diff=device_diff,
        )
