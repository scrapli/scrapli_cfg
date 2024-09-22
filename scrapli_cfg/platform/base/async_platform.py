"""scrapli_cfg.platform.async_platform"""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Callable, List, Optional, Pattern, Tuple, Type

from scrapli.driver import AsyncNetworkDriver
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.exceptions import ScrapliCfgException
from scrapli_cfg.platform.base.base_platform import ScrapliCfgBase
from scrapli_cfg.response import ScrapliCfgResponse


class AsyncScrapliCfgPlatform(ABC, ScrapliCfgBase):
    def __init__(  # pylint: disable=R0917
        self,
        conn: AsyncNetworkDriver,
        config_sources: List[str],
        on_prepare: Optional[Callable[..., Any]],
        dedicated_connection: bool,
        ignore_version: bool,
    ) -> None:
        """
        Scrapli Config async base class

        Args:
            conn: scrapli connection to use
            config_sources: list of config sources
            on_prepare: optional callable to run at connection `prepare`
            dedicated_connection: if `False` (default value) scrapli cfg will not open or close the
                underlying scrapli connection and will raise an exception if the scrapli connection
                is not open. If `True` will automatically open and close the scrapli connection when
                using with a context manager, `prepare` will open the scrapli connection (if not
                already open), and `close` will close the scrapli connection.
            ignore_version: ignore checking device version support; currently this just means that
                scrapli-cfg will not fetch the device version during the prepare phase, however this
                will (hopefully) be used in the future to limit what methods can be used against a
                target device. For example, for EOS devices we need > 4.14 to load configs; so if a
                device is encountered at 4.13 the version check would raise an exception rather than
                just failing in a potentially awkward fashion.

        Returns:
            None

        Raises:
            N/A

        """
        self.conn: AsyncNetworkDriver = conn
        self.dedicated_connection = dedicated_connection

        self.on_prepare = on_prepare

        super().__init__(config_sources=config_sources, ignore_version=ignore_version)

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
        await self.prepare()
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
        await self.cleanup()

    async def _open(self) -> None:
        """
        Handle opening (or raising exception if not open) of underlying scrapli connection

        Args:
            N/A

        Returns:
            None

        Raises:
            ScrapliCfgException: if scrapli connection is not open and auto_open_connection is False

        """
        if self.conn.isalive():
            return

        if self.dedicated_connection:
            self.logger.info(
                "underlying scrapli connection is not alive... opening scrapli connection"
            )
            await self.conn.open()
            return

        raise ScrapliCfgException(
            "underlying scrapli connection is not open and `dedicated_connection` is False, "
            "cannot continue!"
        )

    async def _close(self) -> None:
        """
        Close the scrapli connection

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        if self.dedicated_connection is True and self.conn.isalive():
            self.logger.info("dedicated_connection is True, closing scrapli connection")
            await self.conn.close()

    async def prepare(self) -> None:
        """
        Prepare connection for scrapli_cfg operations

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self.logger.info("preparing scrapli_cfg connection")

        await self._open()

        if self.ignore_version is False:
            self.logger.debug("ignore_version is False, fetching device version")
            version_response = await self.get_version()
            self._validate_and_set_version(version_response=version_response)

        if self.on_prepare is not None:
            self.logger.debug("on_prepare provided, executing now")
            await self.on_prepare(self)

        self._prepared = True

    async def cleanup(self) -> None:
        """
        Cleanup after scrapli-cfg operations

        Generally this can be skipped, however it will be executed if using a context manager. The
        purpose of this method is to close the underlying scrapli connection (if in
        "dedicated_connection" mode), and to reset the internally used `_version_string`, attribute.
        All this is done so that this cfg connection, if re-used later (as in later in that script
        using the same object) starts with a fresh slate.

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        await self._close()

        # reset the version string/prepare flag so we know we need to re-fetch/re-run if user
        # re-opens connection
        self._version_string = ""
        self._prepared = False

        # this has *probably* been reset already, but reset it just in case user re-opens connection
        # we can have a clean slate to work with
        try:
            self._reset_config_session()  # type: ignore
        except AttributeError:
            pass

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
