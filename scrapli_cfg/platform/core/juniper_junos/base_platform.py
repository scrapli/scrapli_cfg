"""scrapli_cfg.platform.core.juniper_junos.base_platform"""
import re
from datetime import datetime
from logging import LoggerAdapter
from typing import Tuple

from scrapli.driver.network.base_driver import PrivilegeLevel
from scrapli_cfg.platform.core.juniper_junos.patterns import (
    EDIT_PATTERN,
    OUTPUT_HEADER_PATTERN,
    VERSION_PATTERN,
)

CONFIG_SOURCES = [
    "running",
]

JUNOS_ADDTL_PRIVS = {
    "shell": (
        PrivilegeLevel(
            pattern=r"^(?!root)%\s?$",
            name="shell",
            previous_priv="exec",
            deescalate="exit",
            escalate="start shell",
            escalate_auth=False,
            escalate_prompt="",
        )
    ),
    # feel like ive had issues w/ root shell in the past... if this all goes well then it can be
    # added back to scrapli core
    "root_shell": (
        PrivilegeLevel(
            pattern=r"^root@%\s?$",
            name="root_shell",
            previous_priv="exec",
            deescalate="exit",
            escalate="start shell user root",
            escalate_auth=True,
            escalate_prompt=r"^[pP]assword:\s?$",
        )
    ),
}


class ScrapliCfgJunosBase:
    logger: LoggerAdapter
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

    def _normalize_source_candidate_configs(self, source_config: str) -> Tuple[str, str]:
        """
        Normalize candidate config and source config so that we can easily diff them

        Args:
            source_config: current config of the source config store

        Returns:
            ScrapliCfgDiff: scrapli cfg diff object

        Raises:
            N/A

        """
        self.logger.debug("normalizing source and candidate configs for diff object")

        source_config = re.sub(pattern=OUTPUT_HEADER_PATTERN, string=source_config, repl="")
        source_config = re.sub(pattern=EDIT_PATTERN, string=source_config, repl="")
        source_config = "\n".join(line for line in source_config.splitlines() if line)
        candidate_config = re.sub(
            pattern=OUTPUT_HEADER_PATTERN, string=self.candidate_config, repl=""
        )
        candidate_config = "\n".join(line for line in candidate_config.splitlines() if line)

        return source_config, candidate_config
