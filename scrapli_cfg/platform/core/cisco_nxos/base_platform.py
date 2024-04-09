"""scrapli_cfg.platform.core.cisco_nxos.base_platform"""

import re
from datetime import datetime
from logging import Logger, LoggerAdapter
from typing import TYPE_CHECKING, List, Tuple, Union

from scrapli.driver.network import AsyncNetworkDriver, NetworkDriver
from scrapli_cfg.exceptions import (
    FailedToFetchSpaceAvailable,
    GetConfigError,
    InsufficientSpaceAvailable,
)
from scrapli_cfg.helper import strip_blank_lines
from scrapli_cfg.platform.core.cisco_nxos.patterns import (
    BYTES_FREE,
    CHECKPOINT_LINE,
    OUTPUT_HEADER_PATTERN,
    VERSION_PATTERN,
)
from scrapli_cfg.response import ScrapliCfgResponse

if TYPE_CHECKING:
    LoggerAdapterT = LoggerAdapter[Logger]  # pylint:disable=E1136
else:
    LoggerAdapterT = LoggerAdapter


CONFIG_SOURCES = [
    "running",
    "startup",
]


class ScrapliCfgNXOSBase:
    logger: LoggerAdapterT
    candidate_config: str
    candidate_config_filename: str
    _replace: bool
    filesystem: str
    _filesystem_space_available_buffer_perc: int

    def _post_get_filesystem_space_available(self, output: str) -> int:
        """
        Handle post "get_filesystem_space_available" operations for parity between sync and async

        Args:
            output: output that was fetched from the device

        Returns:
            int: bytes of space available on filesystem

        Raises:
            FailedToFetchSpaceAvailable: if could not determine space available... duh :)

        """
        self.logger.info("determining space available from device output")

        bytes_available_match = re.search(pattern=BYTES_FREE, string=output)
        if not bytes_available_match:
            msg = "could not determine space available on filesystem"
            self.logger.critical(msg)
            raise FailedToFetchSpaceAvailable(msg)

        return int(bytes_available_match.groupdict()["bytes_available"])

    def _space_available(self, filesystem_bytes_available: int) -> None:
        """
        Space available operations for parity between sync and async

        It seems that the length of the config is near enough 1:1 to the size it takes up
        on the disk... so roll w/ that plus a bit of buffer based on the available buffer perc

        Args:
            filesystem_bytes_available: bytes available on filesystem

        Returns:
            None

        Raises:
            InsufficientSpaceAvailable: if... insufficient space available....

        """
        if filesystem_bytes_available < (
            len(self.candidate_config) / (self._filesystem_space_available_buffer_perc / 100)
        ) + len(self.candidate_config):
            # filesystem has less than candidate config file size + 10% (by default) space, bail out
            msg = (
                f"insufficient space available for candidate config + "
                f"{self._filesystem_space_available_buffer_perc}% (buffer)"
            )
            self.logger.critical(msg)
            raise InsufficientSpaceAvailable(msg)

    @staticmethod
    def _parse_version(device_output: str) -> str:
        """
        Parse version string out of device output

        Args:
            device_output: output from show version command

        Returns:
            str: device version string

        Raises:
            N/A

        """
        version_string_search = re.search(pattern=VERSION_PATTERN, string=device_output)

        if not version_string_search:
            return ""

        version_string = version_string_search.group(0) or ""
        return version_string

    def _reset_config_session(self) -> None:
        """
        Reset config session info

        Resets the candidate config and config session name attributes -- when these are "empty" we
        know there is no current config session

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self.logger.debug("resetting candidate config and config session name")
        self.candidate_config = ""
        self.candidate_config_filename = ""

    @staticmethod
    def _get_config_command(source: str) -> str:
        """
        Return command to use to get config based on the provided source

        Args:
            source: name of the config source, generally running|startup

        Returns:
            str: command to use to fetch the requested config

        Raises:
            N/A

        """
        if source == "running":
            return "show running-config"
        return "show startup-config"

    def _get_diff_command(self, source: str) -> str:
        """
        Generate diff command based on source to diff and filesystem/candidate config name

        Args:
            source: config source to gen diff for

        Returns:
            str: command to use to diff the configuration

        Raises:
            N/A

        """
        if self._replace:
            return (
                f"show diff rollback-patch {source}-config file {self.filesystem}"
                f"{self.candidate_config_filename}"
            )
        return ""

    def _prepare_config_payloads(self, config: str) -> str:
        """
        Prepare a configuration so it can be nicely sent to the device via scrapli

        Args:
            config: configuration to prep

        Returns:
            str: string of config lines to write to candidate config file

        Raises:
            N/A

        """
        # with the "normal" method (the way iosxe does this) it seems to want to stop at 250ish
        # lines... so this works but its kinda wonky... the actual lines we want to put in the text
        # file are enclosed in curly braces for tcl-reasons i guess
        tclsh_filesystem = f"/{self.filesystem.strip(':')}/"
        tclsh_start_file = f'set fl [open "{tclsh_filesystem}{self.candidate_config_filename}" wb+]'
        tcl_config = "\n".join(
            [f"puts -nonewline $fl {{{line}\r}}" for line in config.splitlines()]
        )
        tclsh_end_file = "close $fl"
        final_config = "\n".join((tclsh_start_file, tcl_config, tclsh_end_file))

        return final_config

    def _prepare_load_config(self, config: str, replace: bool) -> str:
        """
        Handle pre "load_config" operations for parity between sync and async

        Args:
            config: candidate config to load
            replace: True/False replace the configuration; passed here so it can be set at the class
                level as we need to stay in config mode and we need to know if we are doing a merge
                or a replace when we go to diff things

        Returns:
            str: string of config to write to candidate config file

        Raises:
            N/A

        """
        self.candidate_config = config

        if not self.candidate_config_filename:
            self.candidate_config_filename = f"scrapli_cfg_{round(datetime.now().timestamp())}"
            self.logger.debug(
                f"candidate config file name will be '{self.candidate_config_filename}'"
            )

        config = self._prepare_config_payloads(config=config)
        self._replace = replace

        return config

    def clean_config(self, config: str) -> str:
        """
        Clean a configuration file of unwanted lines

        Args:
            config: configuration string to "clean"

        Returns:
            str: cleaned configuration string

        Raises:
            N/A

        """
        self.logger.debug("cleaning config file")

        config = re.sub(pattern=CHECKPOINT_LINE, string=config, repl="")
        config = re.sub(pattern=OUTPUT_HEADER_PATTERN, string=config, repl="")
        return strip_blank_lines(config=config)

    def _pre_get_checkpoint(
        self, conn: Union[AsyncNetworkDriver, NetworkDriver]
    ) -> Tuple[ScrapliCfgResponse, List[str]]:
        """
        Handle pre "get_checkpoint" operations for parity between sync and async

        Args:
            conn: connection from the sync or async platform; passed in explicitly to maintain
                typing sanity

        Returns:
            list: list of commands needed to generate checkpoint and show it

        Raises:
            N/A

        """
        self.logger.info("get_checkpoint requested")

        tmp_timestamp = round(datetime.now().timestamp())
        checkpoint_commands = [
            "terminal dont-ask",
            f"checkpoint file {self.filesystem}scrapli_cfg_tmp_{tmp_timestamp}",
            f"show file {self.filesystem}scrapli_cfg_tmp_{tmp_timestamp}",
            f"delete {self.filesystem}scrapli_cfg_tmp_{tmp_timestamp}",
        ]

        response = ScrapliCfgResponse(host=conn.host, raise_for_status_exception=GetConfigError)

        return response, checkpoint_commands
