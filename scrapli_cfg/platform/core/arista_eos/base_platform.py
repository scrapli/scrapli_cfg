"""scrapli_cfg.platform.core.arista_eos.base"""

import json
import re
from datetime import datetime
from logging import Logger, LoggerAdapter
from typing import TYPE_CHECKING, Iterable, List, Tuple, Union

from scrapli.driver import AsyncNetworkDriver, NetworkDriver
from scrapli.response import Response
from scrapli_cfg.exceptions import ScrapliCfgException
from scrapli_cfg.helper import strip_blank_lines
from scrapli_cfg.platform.core.arista_eos.patterns import (
    BANNER_PATTERN,
    END_PATTERN,
    GLOBAL_COMMENT_LINE_PATTERN,
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


class ScrapliCfgEOSBase:
    conn: Union[NetworkDriver, AsyncNetworkDriver]
    logger: LoggerAdapterT
    config_sources: List[str]
    config_session_name: str
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
    def _parse_config_sessions(device_output: str) -> List[str]:
        """
        Parse config session names out of device output

        Args:
            device_output: output from show version command

        Returns:
            list[str]: config session names

        Raises:
            N/A

        """
        try:
            config_session_dict = json.loads(device_output)
        except json.JSONDecodeError:
            return []

        sessions = list(config_session_dict.get("sessions", {}))
        return sessions

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
        # remove comment lines
        config = re.sub(pattern=GLOBAL_COMMENT_LINE_PATTERN, repl="!", string=config)

        # remove "end" at the end of config if present - if its present it will drop scrapli out
        # of the config session which we do not want
        config = re.sub(pattern=END_PATTERN, repl="!", string=config)

        # find all sections that need to be "eagerly" sent
        eager_config = re.findall(pattern=BANNER_PATTERN, string=config)
        for eager_section in eager_config:
            config = config.replace(eager_section, "!")

        joined_eager_config = "\n".join(captured_section for captured_section in eager_config)

        return config, joined_eager_config

    def _prepare_load_config_session_and_payload(self, config: str) -> Tuple[str, str, bool]:
        """
        Prepare the normal and eager payloads and decide if we need to register a config session

        Args:
            config: candidate config to load

        Returns:
            tuple: tuple containing "normal" config elements to send to the device and "eager" mode
                config elements to send to the device (things like banners/macro that require
                scrapli "eager=True"), and lastly a bool indicating if the config session needs to
                be registered on the device

        Raises:
            N/A

        """
        config, eager_config = self._prepare_config_payloads(config=config)

        register_config_session = False
        if not self.config_session_name:
            self.config_session_name = f"scrapli_cfg_{round(datetime.now().timestamp())}"
            self.logger.debug(f"configuration session name will be '{self.config_session_name}'")
            register_config_session = True

        return config, eager_config, register_config_session

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
        self.config_session_name = ""

    def clean_config(self, config: str) -> str:
        """
        Clean a configuration file of unwanted lines

        Args:
            config: configuration string to "clean";  remove all comment lines from both the source
                and candidate configs -- this is only done here pre-diff, so we dont modify the user
                provided candidate config which can totally have those comment lines - we only
                remove "global" (top level) comments though... user comments attached to interfaces
                and the stuff will remain

        Returns:
            str: cleaned configuration string

        Raises:
            N/A

        """
        self.logger.debug("cleaning config file")

        return strip_blank_lines(
            config=re.sub(pattern=GLOBAL_COMMENT_LINE_PATTERN, string=config, repl="")
        )

    def _pre_clear_config_sessions(self) -> ScrapliCfgResponse:
        """
        Handle pre "clear_config_sessions" operations for parity between sync and async

        Args:
            N/A

        Returns:
            ScrapliCfgResponse: new response object to update w/ get results

        Raises:
            N/A

        """
        self.logger.info("clear_config_sessions requested")

        response = ScrapliCfgResponse(
            host=self.conn.host, raise_for_status_exception=ScrapliCfgException
        )

        return response

    def _post_clear_config_sessions(
        self,
        response: ScrapliCfgResponse,
        scrapli_responses: Iterable[Response],
    ) -> ScrapliCfgResponse:
        """
        Handle post "clear_config_sessions" operations for parity between sync and async

        Args:
            response: response object to update
            scrapli_responses: list of scrapli response objects from fetching the version

        Returns:
            ScrapliCfgResponse: response object containing string of the version as the `result`
                attribute

        Raises:
            N/A

        """
        response.record_response(scrapli_responses=scrapli_responses)

        if response.failed:
            msg = "failed to clear device configuration session(s)"
            self.logger.critical(msg)
            response.result = msg
        else:
            response.result = "configuration session(s) cleared"

        return response
