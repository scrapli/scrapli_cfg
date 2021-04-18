"""scrapli_cfg.platform.async_platform"""
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Callable, List, Optional, Pattern, Tuple, Type

from scrapli.driver import AsyncNetworkDriver
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.platform.base.base_platform import ScrapliCfgBase
from scrapli_cfg.response import ScrapliCfgResponse


class AsyncScrapliCfgPlatform(ABC, ScrapliCfgBase):
    def __init__(
        self,
        conn: AsyncNetworkDriver,
        config_sources: List[str],
        on_open: Callable[..., Any],
        preserve_connection: bool,
    ) -> None:
        """
        Scrapli Config async base class

        Args:
            conn: scrapli connection to use
            config_sources: list of config sources
            on_open: async callable to run at connection open
            preserve_connection: if True underlying scrapli connection will *not* be closed when
                the scrapli_cfg object is closed/exited

        Returns:
            None

        Raises:
            N/A

        """
        self.conn: AsyncNetworkDriver = conn
        self.on_open = on_open
        self.preserve_connection = preserve_connection

        super().__init__(config_sources=config_sources)

    async def open(self) -> None:
        """
        Open the connection and prepare for config operations

        Does "normal" scrapli open things, but also runs the _on_open method of scrapli config which
        generally does things like disable console logging

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self.logger.info("opening scrapli connection")

        if not self.conn.isalive():
            await self.conn.open()

        if self._ignore_version is False:
            self.logger.debug("ignore_version is False, fetching device version")
            version_response = await self.get_version()
            self._validate_and_set_version(version_response=version_response)

        self.logger.debug("executing scrapli_cfg on open method")
        await self.on_open(self)

    async def close(self) -> None:
        """
        Close the scrapli connection

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self.logger.info("closing scrapli connection")

        if self.preserve_connection is False and self.conn.isalive():
            await self.conn.close()

    async def __aenter__(self) -> "AsyncScrapliCfgPlatform":
        """
        Enter method for async context manager

        Args:
            N/A

        Returns:
            AsyncScrapliCfg: opened AsyncScrapliCfg object

        Raises:
            N/A

        """
        await self.open()
        return self

    async def __aexit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """
        Exit method to cleanup for async context manager

        Args:
            exception_type: exception type being raised
            exception_value: message from exception being raised
            traceback: traceback from exception being raised

        Returns:
            None

        Raises:
            N/A

        """
        await self.close()

    @abstractmethod
    async def get_version(self) -> ScrapliCfgResponse:
        """
        Get device version string

        Args:
            N/A

        Returns:
            ScrapliCfgResponse: response object where result is the string of the primary version
                (as in the "main" os version) of the device

        Raises:
            N/A

        """

    @abstractmethod
    async def get_config(self, source: str = "running") -> ScrapliCfgResponse:
        """
        Get device configuration

        Args:
            source: name of the config source, generally running|startup

        Returns:
            ScrapliCfgResponse: response object containing string of the target config source as the
                `result` attribute

        Raises:
            N/A

        """

    @abstractmethod
    async def load_config(
        self, config: str, replace: bool = False, **kwargs: Any
    ) -> ScrapliCfgResponse:
        """
        Load configuration to a device

        Args:
            config: string of the configuration to load
            replace: replace the configuration or not, if false configuration will be loaded as a
                merge operation
            kwargs: additional kwargs that the implementing classes may need for their platform,
                see your specific platform for details

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """

    @abstractmethod
    async def abort_config(self) -> ScrapliCfgResponse:
        """
        Abort a configuration -- discards any loaded config

        Args:
            N/A

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """

    @abstractmethod
    async def commit_config(self, source: str = "running") -> ScrapliCfgResponse:
        """
        Commit a loaded configuration

        Args:
            source: name of the config source to commit against, generally running|startup

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """

    @abstractmethod
    async def diff_config(self, source: str = "running") -> ScrapliCfgDiffResponse:
        """
        Diff a loaded configuration against the source config store

        Args:
            source: name of the config source to diff against, generally running|startup -- device
                diffs will generally not care about this argument, but the built in scrapli differ
                will

        Returns:
            ScrapliCfgDiffResponse: scrapli cfg diff object

        Raises:
            N/A

        """

    async def render_substituted_config(
        self,
        config_template: str,
        substitutes: List[Tuple[str, Pattern[str]]],
        source: str = "running",
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
            source: config source to use for the substitution efforts, typically running|startup

        Returns:
            str: substituted/rendered config

        Raises:
            N/A

        """
        self.logger.info("fetching configuration and replacing with provided substitutes")

        source_config = await self.get_config(source=source)
        return self._render_substituted_config(
            config_template=config_template,
            substitutes=substitutes,
            source_config=source_config.result,
        )
