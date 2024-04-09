"""scrapli_cfg.platform.core.juniper_junos.sync_platform"""

from typing import Any, Callable, List, Optional

from scrapli.driver import NetworkDriver
from scrapli.response import MultiResponse, Response
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.exceptions import DiffConfigError
from scrapli_cfg.platform.base.sync_platform import ScrapliCfgPlatform
from scrapli_cfg.platform.core.juniper_junos.base_platform import (
    CONFIG_SOURCES,
    ScrapliCfgJunosBase,
)
from scrapli_cfg.response import ScrapliCfgResponse


class ScrapliCfgJunos(ScrapliCfgPlatform, ScrapliCfgJunosBase):
    def __init__(
        self,
        conn: NetworkDriver,
        *,
        config_sources: Optional[List[str]] = None,
        on_prepare: Optional[Callable[..., Any]] = None,
        filesystem: str = "/config/",
        cleanup_post_commit: bool = True,
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

        self.filesystem = filesystem

        self._replace = False
        self._set = False

        self.candidate_config_filename = ""
        self._in_configuration_session = False

        self.cleanup_post_commit = cleanup_post_commit

    def _delete_candidate_config(self) -> Response:
        """
        Delete candidate config from the filesystem

        Args:
            N/A

        Returns:
            Response: response from deleting the candidate config

        Raises:
            N/A

        """
        delete_result = self.conn.send_config(
            config=f"rm {self.filesystem}{self.candidate_config_filename}",
            privilege_level="root_shell",
        )
        return delete_result

    def get_version(self) -> ScrapliCfgResponse:
        response = self._pre_get_version()

        version_result = self.conn.send_command(command="show version | grep junos:")

        return self._post_get_version(
            response=response,
            scrapli_responses=[version_result],
            result=self._parse_version(device_output=version_result.result),
        )

    def get_config(self, source: str = "running") -> ScrapliCfgResponse:
        response = self._pre_get_config(source=source)

        if self._in_configuration_session is True:
            config_result = self.conn.send_config(config="run show configuration")
        else:
            config_result = self.conn.send_command(command="show configuration")

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
            set: bool indicating config is a "set" style config (ignored if replace is True)

        Args:
            config: string of the configuration to load
            replace: replace the configuration or not, if false configuration will be loaded as a
                merge operation
            kwargs: additional kwargs that the implementing classes may need for their platform,
                see above for junos supported kwargs

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """
        self._set = kwargs.get("set", False)

        response = self._pre_load_config(config=config)

        config = self._prepare_load_config(config=config, replace=replace)

        config_result = self.conn.send_config(config=config, privilege_level="root_shell")

        if self._replace is True:
            load_config = f"load override {self.filesystem}{self.candidate_config_filename}"
        else:
            if self._set is True:
                load_config = f"load set {self.filesystem}{self.candidate_config_filename}"
            else:
                load_config = f"load merge {self.filesystem}{self.candidate_config_filename}"

        load_result = self.conn.send_config(config=load_config)
        self._in_configuration_session = True

        return self._post_load_config(
            response=response,
            scrapli_responses=[config_result, load_result],
        )

    def abort_config(self) -> ScrapliCfgResponse:
        response = self._pre_abort_config(
            session_or_config_file=bool(self.candidate_config_filename)
        )

        rollback_result = self.conn.send_config(config="rollback 0")
        abort_result = self._delete_candidate_config()
        self._reset_config_session()

        return self._post_abort_config(
            response=response, scrapli_responses=[rollback_result, abort_result]
        )

    def commit_config(self, source: str = "running") -> ScrapliCfgResponse:
        scrapli_responses = []
        response = self._pre_commit_config(
            source=source, session_or_config_file=bool(self.candidate_config_filename)
        )

        commit_result = self.conn.send_config(config="commit")
        scrapli_responses.append(commit_result)

        if self.cleanup_post_commit:
            cleanup_result = self._delete_candidate_config()
            scrapli_responses.append(cleanup_result)

        self._reset_config_session()

        return self._post_load_config(
            response=response,
            scrapli_responses=scrapli_responses,
        )

    def diff_config(self, source: str = "running") -> ScrapliCfgDiffResponse:
        scrapli_responses = []
        device_diff = ""
        source_config = ""

        diff_response = self._pre_diff_config(
            source=source, session_or_config_file=bool(self.candidate_config_filename)
        )

        try:
            diff_result = self.conn.send_config(config="show | compare")
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
