"""scrapli_cfg.platform.core.cisco_nxos.async_platform"""

from typing import Any, Callable, List, Optional, Union

from scrapli.driver.core import AsyncNXOSDriver
from scrapli.response import MultiResponse, Response
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.exceptions import DiffConfigError, FailedToDetermineDeviceState
from scrapli_cfg.platform.base.async_platform import AsyncScrapliCfgPlatform
from scrapli_cfg.platform.core.cisco_nxos.base_platform import CONFIG_SOURCES, ScrapliCfgNXOSBase
from scrapli_cfg.response import ScrapliCfgResponse


class AsyncScrapliCfgNXOS(AsyncScrapliCfgPlatform, ScrapliCfgNXOSBase):
    def __init__(
        self,
        conn: AsyncNXOSDriver,
        *,
        config_sources: Optional[List[str]] = None,
        on_prepare: Optional[Callable[..., Any]] = None,
        filesystem: str = "bootflash:",
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
        self._filesystem_space_available_buffer_perc = 10

        self._replace = False

        self.candidate_config_filename = ""

        self.cleanup_post_commit = cleanup_post_commit

    async def _get_filesystem_space_available(self) -> int:
        """
        Get available space on filesystem

        Args:
            N/A

        Returns:
            None

        Raises:
            FailedToDetermineDeviceState: if unable to fetch file filesystem bytes available

        """
        filesystem_size_result = await self.conn.send_command(
            command=f"dir {self.filesystem} | i 'bytes free'"
        )
        if filesystem_size_result.failed:
            raise FailedToDetermineDeviceState("failed to determine space available on filesystem")

        return self._post_get_filesystem_space_available(output=filesystem_size_result.result)

    async def _delete_candidate_config(self) -> MultiResponse:
        """
        Delete candidate config from the filesystem

        Args:
            N/A

        Returns:
            MultiResponse: response from deleting the candidate config

        Raises:
            N/A

        """
        delete_commands = [
            "terminal dont-ask",
            f"delete {self.filesystem}{self.candidate_config_filename}",
        ]
        delete_result = await self.conn.send_commands(commands=delete_commands)
        return delete_result

    async def get_checkpoint(self) -> ScrapliCfgResponse:
        """
        Get device checkpoint file

        Args:
            N/A

        Returns:
            ScrapliCfgResponse: response object containing string of the target config source as the
                `result` attribute

        Raises:
            N/A

        """
        response, checkpoint_commands = self._pre_get_checkpoint(conn=self.conn)

        checkpoint_results = await self.conn.send_commands(commands=checkpoint_commands)

        try:
            checkpoint: str = checkpoint_results[2].result
        except IndexError:
            checkpoint = ""

        return self._post_get_config(
            response=response,
            source="running",
            scrapli_responses=[checkpoint_results],
            result=checkpoint,
        )

    async def get_version(self) -> ScrapliCfgResponse:
        response = self._pre_get_version()

        version_result = await self.conn.send_command(command='show version | i "NXOS: version"')

        return self._post_get_version(
            response=response,
            scrapli_responses=[version_result],
            result=self._parse_version(device_output=version_result.result),
        )

    async def get_config(self, source: str = "running") -> ScrapliCfgResponse:
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
            kwargs: additional kwargs that the implementing classes may need for their platform,
                see above for nxos supported kwargs

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """
        response = self._pre_load_config(config=config)

        config = self._prepare_load_config(config=config, replace=replace)

        filesystem_bytes_available = await self._get_filesystem_space_available()
        self._space_available(filesystem_bytes_available=filesystem_bytes_available)

        await self.conn.acquire_priv(desired_priv="tclsh")
        config_result = await self.conn.send_config(config=config, privilege_level="tclsh")
        await self.conn.acquire_priv(desired_priv=self.conn.default_desired_privilege_level)

        return self._post_load_config(
            response=response,
            scrapli_responses=[config_result],
        )

    async def abort_config(self) -> ScrapliCfgResponse:
        response = self._pre_abort_config(
            session_or_config_file=bool(self.candidate_config_filename)
        )

        abort_result = await self._delete_candidate_config()
        self._reset_config_session()

        return self._post_abort_config(response=response, scrapli_responses=[abort_result])

    async def commit_config(self, source: str = "running") -> ScrapliCfgResponse:
        scrapli_responses: List[Union[MultiResponse, Response]] = []
        response = self._pre_commit_config(
            source=source, session_or_config_file=bool(self.candidate_config_filename)
        )

        if self._replace is True:
            replace_command = (
                f"rollback running-config file {self.filesystem}{self.candidate_config_filename}"
            )
            commit_result = await self.conn.send_command(command=replace_command)
        else:
            merge_command = f"copy {self.filesystem}{self.candidate_config_filename} running-config"
            commit_result = await self.conn.send_command(command=merge_command)

        scrapli_responses.append(commit_result)

        save_config_result = await self.conn.send_command(
            command="copy running-config startup-config"
        )
        scrapli_responses.append(save_config_result)

        if self.cleanup_post_commit:
            cleanup_result = await self._delete_candidate_config()
            scrapli_responses.append(cleanup_result)

        self._reset_config_session()

        return self._post_commit_config(
            response=response,
            scrapli_responses=scrapli_responses,
        )

    async def diff_config(self, source: str = "running") -> ScrapliCfgDiffResponse:
        scrapli_responses = []
        device_diff = ""
        source_config = ""

        diff_response = self._pre_diff_config(
            source=source, session_or_config_file=bool(self.candidate_config_filename)
        )

        try:
            diff_command = self._get_diff_command(source=source)

            if diff_command:
                diff_result = await self.conn.send_command(command=diff_command)
                scrapli_responses.append(diff_result)
                if diff_result.failed:
                    msg = "failed generating diff for config session"
                    self.logger.critical(msg)
                    raise DiffConfigError(msg)
                device_diff = diff_result.result
            else:
                device_diff = ""

            source_config_result = await self.get_config(source=source)
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
