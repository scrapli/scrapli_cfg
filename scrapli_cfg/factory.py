"""scrapli_cfg.factory"""
from typing import TYPE_CHECKING, Any, Callable, List, Optional

from scrapli.driver.core import (
    AsyncEOSDriver,
    AsyncIOSXEDriver,
    AsyncIOSXRDriver,
    AsyncJunosDriver,
    AsyncNXOSDriver,
    EOSDriver,
    IOSXEDriver,
    IOSXRDriver,
    JunosDriver,
    NXOSDriver,
)
from scrapli.driver.network import AsyncNetworkDriver, NetworkDriver
from scrapli_cfg.exceptions import ScrapliCfgException
from scrapli_cfg.logging import logger
from scrapli_cfg.platform.core.arista_eos import AsyncScrapliCfgEOS, ScrapliCfgEOS
from scrapli_cfg.platform.core.cisco_iosxe import AsyncScrapliCfgIOSXE, ScrapliCfgIOSXE
from scrapli_cfg.platform.core.cisco_iosxr import AsyncScrapliCfgIOSXR, ScrapliCfgIOSXR
from scrapli_cfg.platform.core.cisco_nxos import AsyncScrapliCfgNXOS, ScrapliCfgNXOS
from scrapli_cfg.platform.core.juniper_junos import AsyncScrapliCfgJunos, ScrapliCfgJunos

if TYPE_CHECKING:
    from scrapli_cfg.platform.base.async_platform import AsyncScrapliCfgPlatform  # pragma: no cover
    from scrapli_cfg.platform.base.sync_platform import ScrapliCfgPlatform  # pragma: no cover

ASYNC_CORE_PLATFORM_MAP = {
    AsyncEOSDriver: AsyncScrapliCfgEOS,
    AsyncIOSXEDriver: AsyncScrapliCfgIOSXE,
    AsyncIOSXRDriver: AsyncScrapliCfgIOSXR,
    AsyncNXOSDriver: AsyncScrapliCfgNXOS,
    AsyncJunosDriver: AsyncScrapliCfgJunos,
}
SYNC_CORE_PLATFORM_MAP = {
    EOSDriver: ScrapliCfgEOS,
    IOSXEDriver: ScrapliCfgIOSXE,
    IOSXRDriver: ScrapliCfgIOSXR,
    NXOSDriver: ScrapliCfgNXOS,
    JunosDriver: ScrapliCfgJunos,
}


def ScrapliCfg(
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
    logger.debug("ScrapliCfg factory initialized")

    platform_class = SYNC_CORE_PLATFORM_MAP.get(type(conn))
    if not platform_class:
        raise ScrapliCfgException(
            f"scrapli connection object type '{type(conn)}' not a supported scrapli-cfg type"
        )

    final_platform: "ScrapliCfgPlatform" = platform_class(
        conn=conn, config_sources=config_sources, on_open=on_open, **kwargs
    )

    return final_platform


def AsyncScrapliCfg(
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
    logger.debug("AsyncScrapliCfg factory initialized")

    platform_class = ASYNC_CORE_PLATFORM_MAP.get(type(conn))
    if not platform_class:
        raise ScrapliCfgException(
            f"scrapli connection object type '{type(conn)}' not a supported scrapli-cfg type"
        )

    final_platform: "AsyncScrapliCfgPlatform" = platform_class(
        conn=conn, config_sources=config_sources, on_open=on_open, **kwargs
    )

    return final_platform
