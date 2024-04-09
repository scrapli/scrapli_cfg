"""scrapli_cfg.platform.core.cisco_iosxe.sync_platform"""

from typing import Any, Callable, List, Optional

from scrapli.driver import NetworkDriver
from scrapli.response import MultiResponse, Response
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.exceptions import DiffConfigError, FailedToDetermineDeviceState
from scrapli_cfg.platform.base.sync_platform import ScrapliCfgPlatform
from scrapli_cfg.platform.core.cisco_iosxe.base_platform import (
    CONFIG_SOURCES,
    FilePromptMode,
    ScrapliCfgIOSXEBase,
)
from scrapli_cfg.response import ScrapliCfgResponse


class ScrapliCfgIOSXE(ScrapliCfgPlatform, ScrapliCfgIOSXEBase):
    def __init__(
        self,
        conn: NetworkDriver,
        *,
        config_sources: Optional[List[str]] = None,
        on_prepare: Optional[Callable[..., Any]] = None,
        filesystem: str = "flash:",
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

    def _get_filesystem_space_available(self) -> int:
        """
        Abort a configuration -- discards any loaded config

        Args:
            N/A

        Returns:
            None

        Raises:
            FailedToDetermineDeviceState: if unable to fetch file filesystem bytes available

        """
        filesystem_size_result = self.conn.send_command(command=f"dir {self.filesystem} | i bytes")
        if filesystem_size_result.failed:
            raise FailedToDetermineDeviceState("failed to determine space available on filesystem")

        return self._post_get_filesystem_space_available(output=filesystem_size_result.result)

    def _determine_file_prompt_mode(self) -> FilePromptMode:
        """
        Determine the device file prompt mode

        Args:
            N/A

        Returns:
            FilePromptMode: enum representing file prompt mode

        Raises:
            FailedToDetermineDeviceState: if unable to fetch file prompt mode

        """
        file_prompt_mode_result = self.conn.send_command(command="show run | i file prompt")
        if file_prompt_mode_result.failed:
            raise FailedToDetermineDeviceState("failed to determine file prompt mode")

        return self._post_determine_file_prompt_mode(output=file_prompt_mode_result.result)

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
        # have to check again because the candidate config may have changed this!
        file_prompt_mode = self._determine_file_prompt_mode()
        if file_prompt_mode in (FilePromptMode.ALERT, FilePromptMode.NOISY):
            delete_events = [
                (
                    f"delete {self.filesystem}{self.candidate_config_filename}",
                    "Delete filename",
                ),
                (
                    "",
                    "[confirm]",
                ),
                ("", ""),
            ]
        else:
            delete_events = [
                (f"delete {self.filesystem}{self.candidate_config_filename}", "[confirm]"),
                ("", ""),
            ]
        delete_result = self.conn.send_interactive(interact_events=delete_events)
        return delete_result

    def get_version(self) -> ScrapliCfgResponse:
        response = self._pre_get_version()

        version_result = self.conn.send_command(command="show version | i Version")

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
            auto_clean: automatically "clean" any data that would be in a configuration from a
                "get_config" operation that would prevent loading a config -- for example, things
                like the "Building Configuration" lines in IOSXE output, etc.. Defaults to `True`

        Args:
            config: string of the configuration to load
            replace: replace the configuration or not, if false configuration will be loaded as a
                merge operation
            kwargs: additional kwargs that the implementing classes may need for their platform,
                see above for iosxe supported kwargs

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """
        if kwargs.get("auto_clean", True) is True:
            config = self.clean_config(config=config)

        response = self._pre_load_config(config=config)

        config = self._prepare_load_config(config=config, replace=replace)

        filesystem_bytes_available = self._get_filesystem_space_available()
        self._space_available(filesystem_bytes_available=filesystem_bytes_available)

        # when in tcl command mode or whatever it is, tcl wants \r for return char, so stash the
        # original return char and sub in \r for a bit
        original_return_char = self.conn.comms_return_char
        tcl_comms_return_char = "\r"

        # pop into tclsh before swapping the return char just to be safe -- \r or \n should both be
        # fine for up to here but who knows... :)
        self.conn.acquire_priv(desired_priv="tclsh")
        self.conn.comms_return_char = tcl_comms_return_char
        config_result = self.conn.send_config(config=config, privilege_level="tclsh")

        # reset the return char to the "normal" one and drop into whatever is the "default" priv
        self.conn.acquire_priv(desired_priv=self.conn.default_desired_privilege_level)
        self.conn.comms_return_char = original_return_char

        return self._post_load_config(
            response=response,
            scrapli_responses=[config_result],
        )

    def abort_config(self) -> ScrapliCfgResponse:
        response = self._pre_abort_config(
            session_or_config_file=bool(self.candidate_config_filename)
        )

        abort_result = self._delete_candidate_config()
        self._reset_config_session()

        return self._post_abort_config(response=response, scrapli_responses=[abort_result])

    def save_config(self) -> Response:
        """
        Save the config -- "copy run start"!

        Args:
             N/A

        Returns:
            Response: scrapli response object

        Raises:
            N/A

        """
        # we always re-check file prompt mode because it could have changed!
        file_prompt_mode = self._determine_file_prompt_mode()

        if file_prompt_mode == FilePromptMode.ALERT:
            save_events = [
                (
                    "copy running-config startup-config",
                    "Destination filename",
                ),
                ("", ""),
            ]
        elif file_prompt_mode == FilePromptMode.NOISY:
            save_events = [
                (
                    "copy running-config startup-config",
                    "Source filename",
                ),
                (
                    "",
                    "Destination filename",
                ),
                ("", ""),
            ]
        else:
            save_events = [("copy running-config startup-config", "")]

        save_result = self.conn.send_interactive(interact_events=save_events)
        return save_result

    def _commit_config_merge(self, file_prompt_mode: Optional[FilePromptMode] = None) -> Response:
        """
        Commit the configuration in merge mode

        Args:
             file_prompt_mode: optionally provide the file prompt mode, if its None we will fetch it
                 to decide if we need to use interactive mode or not

        Returns:
            Response: scrapli response object

        Raises:
            N/A

        """
        if file_prompt_mode is None:
            file_prompt_mode = self._determine_file_prompt_mode()

        if file_prompt_mode == FilePromptMode.ALERT:
            merge_events = [
                (
                    f"copy {self.filesystem}{self.candidate_config_filename} running-config",
                    "Destination filename",
                ),
                ("", ""),
            ]
        elif file_prompt_mode == FilePromptMode.NOISY:
            merge_events = [
                (
                    f"copy {self.filesystem}{self.candidate_config_filename} running-config",
                    "Source filename",
                ),
                (
                    "",
                    "Destination filename",
                ),
                ("", ""),
            ]
        else:
            merge_events = [
                (f"copy {self.filesystem}{self.candidate_config_filename} running-config", "")
            ]

        commit_result = self.conn.send_interactive(interact_events=merge_events)
        return commit_result

    def commit_config(self, source: str = "running") -> ScrapliCfgResponse:
        scrapli_responses = []
        response = self._pre_commit_config(
            source=source, session_or_config_file=bool(self.candidate_config_filename)
        )

        file_prompt_mode = self._determine_file_prompt_mode()

        if self._replace is True:
            replace_command = (
                f"configure replace {self.filesystem}{self.candidate_config_filename} force"
            )
            commit_result = self.conn.send_command(command=replace_command)
        else:
            commit_result = self._commit_config_merge(file_prompt_mode=file_prompt_mode)

        scrapli_responses.append(commit_result)

        save_config_result = self.save_config()
        scrapli_responses.append(save_config_result)

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
            diff_result = self.conn.send_command(command=self._get_diff_command(source=source))
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
