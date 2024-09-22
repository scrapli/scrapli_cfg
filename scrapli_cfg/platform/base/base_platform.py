"""scrapli_cfg.platforms.base_platform"""

import re
from typing import List, Pattern, Tuple, Union

from scrapli.driver import AsyncNetworkDriver, NetworkDriver
from scrapli.logging import get_instance_logger
from scrapli.response import MultiResponse, Response
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.exceptions import (
    AbortConfigError,
    CommitConfigError,
    DiffConfigError,
    GetConfigError,
    InvalidConfigTarget,
    LoadConfigError,
    PrepareNotCalled,
    TemplateError,
    VersionError,
)
from scrapli_cfg.response import ScrapliCfgResponse


class ScrapliCfgBase:
    conn: Union[NetworkDriver, AsyncNetworkDriver]

    def __init__(self, config_sources: List[str], ignore_version: bool = False) -> None:
        """
        Base class for all CFG platforms

        Args:
            config_sources: list of allowed config sources
            ignore_version: ignore platform version check or not

        Returns:
            None

        Raises:
            N/A

        """
        self.logger = get_instance_logger(
            instance_name="scrapli_cfg.platform", host=self.conn.host, port=self.conn.port
        )

        self.config_sources = config_sources
        self.candidate_config = ""

        self.ignore_version = ignore_version
        self._get_version_command = ""
        self._version_string = ""

        # bool indicated if a `on_prepare` callable has been executed or not
        self._prepared = False

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
            msg = "failed getting version from device"
            self.logger.critical(msg)
            raise VersionError(msg)
        if not version_response.result:
            msg = "failed parsing version string from device output"
            self.logger.critical(msg)
            raise VersionError(msg)
        self._version_string = version_response.result

    def _prepare_ok(self) -> None:
        """
        Determine if prepare is "OK" for a given operation

        Checks if an `on_prepare` callable has been provided, and if so, if it has been executed.
        This is meant to help force users into calling `prepare` or using the context manager prior
        to running any methods.

        Args:
            N/A

        Returns:
            None

        Raises:
            PrepareNotCalled: if `on_prepare` is not None and `_prepared` is False

        """
        # ignoring type/complaints as `on_prepare` will always be set in the sync/async classes;
        # but is not set here since in one its a coroutine and the other not
        _on_prepare = self.on_prepare  # type: ignore  # pylint:disable=E1101
        if _on_prepare is not None and self._prepared is False:
            raise PrepareNotCalled(
                "on_prepare callable provided, but prepare method not called. call prepare method "
                "or use context manager to ensure it is called for you"
            )

    def _version_ok(self) -> None:
        """
        Determine if version is "OK" for a given operation

        Should be overridden and super'd to by platforms that implement version constraints, will
        simply check that if `ignore_version` is `False` we have set the internal `_version_string`
        attribute, if not, will raise `PrepareNotCalled` exception.

        Args:
            N/A

        Returns:
            None

        Raises:
            PrepareNotCalled: if ignore version is False and _version_string not set

        """
        if self.ignore_version is False and not self._version_string:
            raise PrepareNotCalled(
                "ignore_version is False, but version has not yet been fetched. call prepare method"
                " or use context manager to ensure that version is properly gathered"
            )

    def _operation_ok(self) -> None:
        """
        Determine if all values are "OK" for a given operation

        Checks if version and prepare are ok. Convenience func to just have one thing to call in the
        `_pre` operation methods.

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self._prepare_ok()
        self._version_ok()

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

        self._operation_ok()

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
        scrapli_responses: List[Union[Response, MultiResponse]],
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

        self._operation_ok()

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

        self._operation_ok()

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
        scrapli_responses: List[Union[Response, MultiResponse]],
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

        self._operation_ok()

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
        scrapli_responses: List[Union[Response, MultiResponse]],
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

        self._operation_ok()

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

    def _post_diff_config(  # pylint: disable=R0917
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
            source_config=source_config + "\n",
            candidate_config=candidate_config + "\n",
            device_diff=device_diff,
        )

        if diff_response.failed:
            msg = "failed to diff config"
            self.logger.critical(msg)

        return diff_response
