"""scrapli_cfg.factory"""
from typing import TYPE_CHECKING, Any, Callable, List, Optional

from scrapli.driver.network import AsyncNetworkDriver, NetworkDriver
from scrapli_cfg.exceptions import ScrapliCfgException
from scrapli_cfg.logging import logger
from scrapli_cfg.platform.core.arista_eos import AsyncScrapliCfgEOS, ScrapliCfgEOS
from scrapli_cfg.platform.core.cisco_iosxe import AsyncScrapliCfgIOSXE, ScrapliCfgIOSXE
from scrapli_cfg.platform.core.cisco_iosxr import AsyncScrapliCfgIOSXR, ScrapliCfgIOSXR
from scrapli_cfg.platform.core.cisco_nxos import AsyncScrapliCfgNXOS, ScrapliCfgNXOS

if TYPE_CHECKING:
    from scrapli_cfg.platform.base.async_platform import AsyncScrapliCfgPlatform
    from scrapli_cfg.platform.base.sync_platform import ScrapliCfgPlatform

ASYNC_CORE_PLATFORM_MAP = {
    "arista_eos": AsyncScrapliCfgEOS,
    "cisco_iosxe": AsyncScrapliCfgIOSXE,
    "cisco_iosxr": AsyncScrapliCfgIOSXR,
    "cisco_nxos": AsyncScrapliCfgNXOS,
}
SYNC_CORE_PLATFORM_MAP = {
    "arista_eos": ScrapliCfgEOS,
    "cisco_iosxe": ScrapliCfgIOSXE,
    "cisco_iosxr": ScrapliCfgIOSXR,
    "cisco_nxos": ScrapliCfgNXOS,
}


def ScrapliCfg(
    platform: str,
    conn: NetworkDriver,
    config_sources: Optional[List[str]] = None,
    on_open: Optional[Callable[..., Any]] = None,
    **kwargs: Any,
) -> "ScrapliCfgPlatform":
    """
    Scrapli Config Sync Factory

    Return a sync scrapli config object for the provided platform. Prefer to use factory classes
    just so that the naming convention (w/ upper case things) is "right", but given that the class
    version inherited from the base ScrapliCfgPlatform and did not implement the abstract methods
    this felt like a better move.

    Args:
        platform: string name of platform -- i.e. cisco_iosxe, arista_eos
        conn: scrapli connection to use
        config_sources: list of config sources
        on_open: async callable to run at connection open
        kwargs: keyword args to pass to the scrapli_cfg object (for things like iosxe 'filesystem'
            argument)

    Returns:
        ScrapliCfg: sync scrapli cfg object

    Raises:
        ScrapliCfgException: if platform is not a string

    """
    logger.debug("Scrapli factory initialized")

    if not isinstance(platform, str):
        raise ScrapliCfgException(f"Argument 'platform' must be 'str' got '{type(platform)}'")

    platform_class = SYNC_CORE_PLATFORM_MAP.get(platform)
    if not platform_class:
        raise ScrapliCfgException(f"platform '{platform}' not a valid platform name")

    final_platform: "ScrapliCfgPlatform" = platform_class(
        conn=conn, config_sources=config_sources, on_open=on_open, **kwargs
    )

    return final_platform


def AsyncScrapliCfg(
    platform: str,
    conn: AsyncNetworkDriver,
    config_sources: Optional[List[str]] = None,
    on_open: Optional[Callable[..., Any]] = None,
    **kwargs: Any,
) -> "AsyncScrapliCfgPlatform":
    """
    Scrapli Config Async Factory

    Return a async scrapli config object for the provided platform. Prefer to use factory classes
    just so that the naming convention (w/ upper case things) is "right", but given that the class
    version inherited from the base ScrapliCfgPlatform and did not implement the abstract methods
    this felt like a better move.

    Args:
        platform: string name of platform -- i.e. cisco_iosxe, arista_eos
        conn: scrapli connection to use
        config_sources: list of config sources
        on_open: async callable to run at connection open
        kwargs: keyword args to pass to the scrapli_cfg object (for things like iosxe 'filesystem'
            argument)

    Returns:
        AsyncScrapliCfg: async scrapli cfg object

    Raises:
        ScrapliCfgException: if platform is not a string

    """
    logger.debug("Scrapli factory initialized")

    if not isinstance(platform, str):
        raise ScrapliCfgException(f"Argument 'platform' must be 'str' got '{type(platform)}'")

    platform_class = ASYNC_CORE_PLATFORM_MAP.get(platform)
    if not platform_class:
        raise ScrapliCfgException(f"platform '{platform}' not a valid platform name")

    final_platform: "AsyncScrapliCfgPlatform" = platform_class(
        conn=conn, config_sources=config_sources, on_open=on_open, **kwargs
    )

    return final_platform
