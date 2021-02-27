"""scrapli_cfg.platforms.base_platform"""
import re
from typing import List, Pattern, Tuple, Union

from scrapli.driver import AsyncNetworkDriver, NetworkDriver
from scrapli.logging import get_instance_logger
from scrapli.response import Response
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.exceptions import (
    AbortConfigError,
    CommitConfigError,
    DiffConfigError,
    GetConfigError,
    InvalidConfigTarget,
    LoadConfigError,
    TemplateError,
    VersionError,
)
from scrapli_cfg.response import ScrapliCfgResponse


class ScrapliCfgBase:
    conn: Union[NetworkDriver, AsyncNetworkDriver]

    def __init__(self, config_sources: List[str], ignore_version: bool = False) -> None:
        self.logger = get_instance_logger(
            instance_name="scrapli_cfg.platform", host=self.conn.host, port=self.conn.port
        )

        self.config_sources = config_sources
        self.candidate_config = ""

        self._ignore_version = ignore_version
        self._get_version_command = ""
        self._version_string = ""

    def _render_substituted_config(
        self, config_template: str, substitutes: List[Tuple[str, Pattern[str]]], source_config: str
    ) -> str:
        """
        Render a substituted configuration file

        Renders a configuration based on a user template, substitutes, and a target config from the
        device.

        Args:
            config_template: config file to use as the base for substitutions -- should contain
                jinja2-like variables that will be replaced with data fetched from the source config
                by the substitutes patterns
            substitutes: tuple of name, pattern -- where name matches the jinja2-like variable in
                the config_template file, and pattern is a compiled regular expression pattern to be
                used to fetch that section from the source config
            source_config: current source config to use in substitution process

        Returns:
            None

        Raises:
            TemplateError: if no substitute sections are provided
            TemplateError: if one or more of the substitute sections is missing in the template
            TemplateError: if a substitute pattern is not found in the config template

        """
        self.logger.debug("rendering substituted config")

        if not substitutes:
            msg = "no substitutes provided..."
            self.logger.critical(msg)
            raise TemplateError(msg)

        if not all(f"{{{{ {name} }}}}" in config_template for name, _ in substitutes):
            msg = "missing one or more of the provided substitutions from the config template"
            self.logger.critical(msg)
            raise TemplateError(msg)

        replace_sections = [
            (name, re.search(pattern=pattern, string=source_config))
            for name, pattern in substitutes
        ]

        rendered_config = ""
        for name, replace_section in replace_sections:
            if not replace_section:
                msg = (
                    f"substitution pattern {name} was unable to find a match in the target config"
                    " source"
                )
                self.logger.critical(msg)
                raise TemplateError(msg)

            replace_group = replace_section.group()
            rendered_config = config_template.replace(f"{{{{ {name} }}}}", replace_group)

        # remove any totally empty lines (from bad regex, or just device spitting out lines w/
        # nothing on it
        rendered_config = "\n".join(line for line in rendered_config.splitlines() if line)

        self.logger.debug("rendering substituted config complete")

        return rendered_config

    def _validate_and_set_version(self, version_response: ScrapliCfgResponse) -> None:
        """
        Ensure version was fetched successfully and set internal version attribute

        Args:
            version_response: scrapli cfg response from get version operation

        Returns:
            None

        Raises:
            VersionError: if fetching version failed or failed to parse version

        """
        if version_response.failed:
            msg = "getting version from device failed"
            self.logger.critical(msg)
            raise VersionError(msg)
        if not version_response.result:
            msg = "failed parsing version string from device output"
            self.logger.critical(msg)
            raise VersionError(msg)
        self._version_string = version_response.result

    def _pre_get_version(self) -> ScrapliCfgResponse:
        """
        Handle pre "get_version" operations for parity between sync and async

        Args:
            N/A

        Returns:
            ScrapliCfgResponse: new response object to update w/ get results

        Raises:
            N/A

        """
        self.logger.info("get_version requested")

        response = ScrapliCfgResponse(host=self.conn.host, raise_for_status_exception=VersionError)

        return response

    def _post_get_version(
        self,
        response: ScrapliCfgResponse,
        scrapli_responses: List[Response],
        result: str,
    ) -> ScrapliCfgResponse:
        """
        Handle post "get_version" operations for parity between sync and async

        Args:
            response: response object to update
            scrapli_responses: list of scrapli response objects from fetching the version
            result: final version string of the device

        Returns:
            ScrapliCfgResponse: response object containing string of the version as the `result`
                attribute

        Raises:
            N/A

        """
        response.record_response(scrapli_responses=scrapli_responses, result=result)

        if response.failed:
            msg = "failed to get version from device"
            self.logger.critical(msg)

        return response

    def _pre_get_config(self, source: str) -> ScrapliCfgResponse:
        """
        Handle pre "get_config" operations for parity between sync and async

        Args:
            source: name of the config source, generally running|startup

        Returns:
            ScrapliCfgResponse: new response object to update w/ get results

        Raises:
            InvalidConfigTarget: if the requested config source is not valid

        """
        self.logger.info(f"get_config for config source '{source}' requested")

        if source not in self.config_sources:
            msg = (
                f"provided config source '{source}' not valid, must be one of {self.config_sources}"
            )
            self.logger.critical(msg)
            raise InvalidConfigTarget(msg)

        response = ScrapliCfgResponse(
            host=self.conn.host, raise_for_status_exception=GetConfigError
        )

        return response

    def _post_get_config(
        self,
        response: ScrapliCfgResponse,
        source: str,
        scrapli_responses: List[Response],
        result: str,
    ) -> ScrapliCfgResponse:
        """
        Handle post "get_config" operations for parity between sync and async

        Args:
            response: response object to update
            source: name of the config source, generally running|startup
            scrapli_responses: list of scrapli response objects from fetching the config
            result: final string of the "get_config" result

        Returns:
            ScrapliCfgResponse: response object containing string of the target config source as the
                `result` attribute

        Raises:
            N/A

        """
        response.record_response(scrapli_responses=scrapli_responses, result=result)

        if response.failed:
            msg = f"failed to get {source} config"
            self.logger.critical(msg)

        return response

    def _pre_load_config(self, config: str) -> ScrapliCfgResponse:
        """
        Handle pre "load_config" operations for parity between sync and async

        Args:
            config: candidate config to load

        Returns:
            ScrapliCfgResponse: new response object for load operation

        Raises:
            N/A

        """
        self.logger.info("load_config requested")

        self.candidate_config = config

        response = ScrapliCfgResponse(
            host=self.conn.host, raise_for_status_exception=LoadConfigError
        )

        return response

    def _post_load_config(
        self,
        response: ScrapliCfgResponse,
        scrapli_responses: List[Response],
    ) -> ScrapliCfgResponse:
        """
        Handle post "get_config" operations for parity between sync and async

        Args:
            response: response object to update
            scrapli_responses: list of scrapli response objects from fetching the config

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """
        response.record_response(scrapli_responses=scrapli_responses)

        if response.failed:
            msg = "failed to load candidate config"
            self.logger.critical(msg)

        return response

    def _pre_abort_config(self, session_or_config_file: bool) -> ScrapliCfgResponse:
        """
        Handle pre "abort_config" operations for parity between sync and async

        Args:
            session_or_config_file: bool indicating if a session or candidate config file has been
                loaded -- in other words, is there anything to abort right now

        Returns:
            ScrapliCfgResponse: response object for abort operation

        Raises:
            AbortConfigError: if no config session or config file exists then we have no config to
                abort!

        """
        self.logger.info("abort_config requested")

        if session_or_config_file is False:
            msg = (
                "no configuration session or candidate configuration file exists, you must load a "
                "config in order to abort it!"
            )
            self.logger.critical(msg)
            raise AbortConfigError(msg)

        response = ScrapliCfgResponse(
            host=self.conn.host, raise_for_status_exception=AbortConfigError
        )

        return response

    def _post_abort_config(
        self,
        response: ScrapliCfgResponse,
        scrapli_responses: List[Response],
    ) -> ScrapliCfgResponse:
        """
        Handle post "abort_config" operations for parity between sync and async

        Args:
            response: response object to update
            scrapli_responses: list of scrapli response objects from aborting the config

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """
        response.record_response(scrapli_responses=scrapli_responses)

        if response.failed:
            msg = "failed to abort config"
            self.logger.critical(msg)

        return response

    def _pre_commit_config(self, source: str, session_or_config_file: bool) -> ScrapliCfgResponse:
        """
        Handle pre "commit_config" operations for parity between sync and async

        Args:
            source: name of the config source, generally running|startup
            session_or_config_file: bool indicating if a session or candidate config file has been
                loaded -- in other words, is there anything to commit right now

        Returns:
            ScrapliCfgResponse: new response object to update w/ commit results

        Raises:
            InvalidConfigTarget: if the requested config source is not valid
            CommitConfigError: if no config session/file exists to commit

        """
        self.logger.info(f"get_config for config source '{source}' requested")

        if source not in self.config_sources:
            msg = (
                f"provided config source '{source}' not valid, must be one of {self.config_sources}"
            )
            self.logger.critical(msg)
            raise InvalidConfigTarget(msg)

        if session_or_config_file is False:
            msg = (
                "no configuration session or candidate configuration file exists, you must load a "
                "config in order to commit it!"
            )
            self.logger.critical(msg)
            raise CommitConfigError(msg)

        response = ScrapliCfgResponse(
            host=self.conn.host, raise_for_status_exception=CommitConfigError
        )

        return response

    def _post_commit_config(
        self,
        response: ScrapliCfgResponse,
        scrapli_responses: List[Response],
    ) -> ScrapliCfgResponse:
        """
        Handle post "commit_config" operations for parity between sync and async

        Args:
            response: response object to update
            scrapli_responses: list of scrapli response objects from committing the config

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """
        response.record_response(scrapli_responses=scrapli_responses)

        if response.failed:
            msg = "failed to commit config"
            self.logger.critical(msg)

        return response

    def _pre_diff_config(self, source: str, session_or_config_file: bool) -> ScrapliCfgDiffResponse:
        """
        Handle pre "diff_config" operations for parity between sync and async

        Args:
            source: config source to diff against
            session_or_config_file: bool of config_session_name or candidate_config_filename

        Returns:
            ScrapliCfgDiffResponse: diff object for diff operation

        Raises:
            InvalidConfigTarget: if trying to diff against an invalid config target
            DiffConfigError: if no config session or config file exists then we have no config to
                diff!

        """
        self.logger.info("diff_config requested")

        if source not in self.config_sources:
            msg = (
                f"provided config source '{source}' not valid, must be one of {self.config_sources}"
            )
            self.logger.critical(msg)
            raise InvalidConfigTarget(msg)

        if session_or_config_file is False:
            msg = (
                "no configuration session or candidate configuration file exists, you must load a "
                "config in order to diff it!"
            )
            self.logger.critical(msg)
            raise DiffConfigError(msg)

        diff_response = ScrapliCfgDiffResponse(host=self.conn.host, source=source)

        return diff_response

    def _post_diff_config(
        self,
        diff_response: ScrapliCfgDiffResponse,
        scrapli_responses: List[Response],
        source_config: str,
        candidate_config: str,
        device_diff: str,
    ) -> ScrapliCfgDiffResponse:
        """
        Handle post "diff_config" operations for parity between sync and async

        Args:
            diff_response: response object to update
            scrapli_responses: list of scrapli response objects from committing the config
            source_config: previous source config from the device
            candidate_config: user provided configuration
            device_diff: diff generated from the device itself

        Returns:
            ScrapliCfgDiffResponse: diff object for diff operation

        Raises:
            N/A

        """
        diff_response.record_response(scrapli_responses=scrapli_responses)
        diff_response.record_diff_response(
            source_config=source_config, candidate_config=candidate_config, device_diff=device_diff
        )

        if diff_response.failed:
            msg = "failed to diff config"
            self.logger.critical(msg)

        return diff_response
