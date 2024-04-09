"""scrapli_cfg.platform.core.juniper_junos.base_platform"""

import re
from datetime import datetime
from logging import Logger, LoggerAdapter
from typing import TYPE_CHECKING

from scrapli_cfg.helper import strip_blank_lines
from scrapli_cfg.platform.core.juniper_junos.patterns import (
    EDIT_PATTERN,
    OUTPUT_HEADER_PATTERN,
    VERSION_PATTERN,
)

if TYPE_CHECKING:
    LoggerAdapterT = LoggerAdapter[Logger]  # pylint:disable=E1136
else:
    LoggerAdapterT = LoggerAdapter


CONFIG_SOURCES = [
    "running",
]


class ScrapliCfgJunosBase:
    logger: LoggerAdapterT
    candidate_config: str
    candidate_config_filename: str
    _in_configuration_session: bool
    _replace: bool
    _set: bool
    filesystem: str

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
        self.logger.debug("resetting candidate config and candidate config file name")
        self.candidate_config = ""
        self.candidate_config_filename = ""
        self._in_configuration_session = False
        self._set = False

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
        final_config_list = []
        for config_line in config.splitlines():
            final_config_list.append(
                f"echo >> {self.filesystem}{self.candidate_config_filename} '{config_line}'"
            )

        final_config = "\n".join(final_config_list)

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

        config = re.sub(pattern=OUTPUT_HEADER_PATTERN, string=config, repl="")
        config = re.sub(pattern=EDIT_PATTERN, string=config, repl="")
        return strip_blank_lines(config=config)
