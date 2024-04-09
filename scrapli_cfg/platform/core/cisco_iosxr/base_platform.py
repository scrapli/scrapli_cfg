"""scrapli_cfg.platform.core.cisco_iosxr.base_platform"""

import re
from logging import Logger, LoggerAdapter
from typing import TYPE_CHECKING, Tuple

from scrapli_cfg.helper import strip_blank_lines
from scrapli_cfg.platform.core.cisco_iosxr.patterns import (
    BANNER_PATTERN,
    END_PATTERN,
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


class ScrapliCfgIOSXRBase:
    logger: LoggerAdapterT
    _in_configuration_session: bool
    _config_privilege_level: str
    _replace: bool
    candidate_config: str

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

    @staticmethod
    def _prepare_config_payloads(config: str) -> Tuple[str, str]:
        """
        Prepare a configuration so it can be nicely sent to the device via scrapli

        Args:
            config: configuration to prep

        Returns:
            tuple: tuple of "normal" config lines and "eager" config lines

        Raises:
            N/A

        """
        # remove building config lines
        config = re.sub(pattern=OUTPUT_HEADER_PATTERN, repl="!", string=config)

        # remove "end" at the end of config if present - if its present it will drop scrapli out
        # of the config session which we do not want
        config = re.sub(pattern=END_PATTERN, repl="!", string=config)

        # find all sections that need to be "eagerly" sent
        eager_config = re.findall(pattern=BANNER_PATTERN, string=config)

        for eager_section in eager_config:
            # afaik cant backreference a non capturing group so we have an extra group per match
            # that we ignore here (element 1)
            config = config.replace(eager_section[0], "!")

        joined_eager_config = "\n".join(captured_section[0] for captured_section in eager_config)

        return config, joined_eager_config

    def _prepare_load_config_session_and_payload(
        self, config: str, replace: bool, exclusive: bool
    ) -> Tuple[str, str]:
        """
        Handle pre "load_config" operations for parity between sync and async

        Args:
            config: candidate config to load
            replace: True/False replace the configuration; passed here so it can be set at the class
                level as we need to stay in config mode and we need to know if we are doing a merge
                or a replace when we go to diff things
            exclusive: True/False use exclusive config mode

        Returns:
            tuple: tuple containing "normal" config elements to send to the device and "eager" mode
                config elements to send to the device (things like banners/macro that require
                scrapli "eager=True")

        Raises:
            N/A

        """
        self.candidate_config = config
        config, eager_config = self._prepare_config_payloads(config=config)

        self._in_configuration_session = True
        self._config_privilege_level = "configuration_exclusive" if exclusive else "configuration"
        self._replace = replace

        return config, eager_config

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
        self._in_configuration_session = False
        self._config_privilege_level = "configuration"

    def _get_diff_command(self) -> str:
        """
        Generate diff command based on source to diff and filesystem/candidate config name

        Args:
            N/A

        Returns:
            str: command to use to diff the configuration

        Raises:
            N/A

        """
        if self._replace:
            return "show configuration changes diff"
        return "show commit changes diff"

    def clean_config(self, config: str) -> str:
        """
        Clean a configuration file of unwanted lines

        Args:
            config: configuration string to "clean"; cleaning removes leading timestamp/building
                config/xr version/last change lines.

        Returns:
            str: cleaned configuration string

        Raises:
            N/A

        """
        self.logger.debug("cleaning config file")

        # remove any of the leading timestamp/building config/xr version/last change lines in
        # both the source and candidate configs so they dont need to be compared
        return strip_blank_lines(
            config=re.sub(pattern=OUTPUT_HEADER_PATTERN, string=config, repl="")
        )
