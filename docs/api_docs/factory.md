<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.factory

scrapli_cfg.factory

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
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
    *,
    config_sources: Optional[List[str]] = None,
    on_prepare: Optional[Callable[..., Any]] = None,
    dedicated_connection: bool = False,
    ignore_version: bool = False,
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
        kwargs: keyword args to pass to the scrapli_cfg object (for things like iosxe 'filesystem'
            argument)

    Returns:
        ScrapliCfg: sync scrapli cfg object

    Raises:
        ScrapliCfgException: if provided connection object is async
        ScrapliCfgException: if provided connection object is sync but is not a supported ("core")
            platform type

    """
    logger.debug("ScrapliCfg factory initialized")

    if isinstance(conn, AsyncNetworkDriver):
        raise ScrapliCfgException(
            "provided scrapli connection is sync but using 'AsyncScrapliCfg' -- you must use an "
            "async connection with 'AsyncScrapliCfg'!"
        )

    platform_class = SYNC_CORE_PLATFORM_MAP.get(type(conn))
    if not platform_class:
        raise ScrapliCfgException(
            f"scrapli connection object type '{type(conn)}' not a supported scrapli-cfg type"
        )

    final_platform: "ScrapliCfgPlatform" = platform_class(
        conn=conn,
        config_sources=config_sources,
        on_prepare=on_prepare,
        dedicated_connection=dedicated_connection,
        ignore_version=ignore_version,
        **kwargs,
    )

    return final_platform


def AsyncScrapliCfg(
    conn: AsyncNetworkDriver,
    *,
    config_sources: Optional[List[str]] = None,
    on_prepare: Optional[Callable[..., Any]] = None,
    dedicated_connection: bool = False,
    ignore_version: bool = False,
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
        kwargs: keyword args to pass to the scrapli_cfg object (for things like iosxe 'filesystem'
            argument)

    Returns:
        AsyncScrapliCfg: async scrapli cfg object

    Raises:
        ScrapliCfgException: if provided connection object is sync
        ScrapliCfgException: if provided connection object is async but is not a supported ("core")
            platform type

    """
    logger.debug("AsyncScrapliCfg factory initialized")

    if isinstance(conn, NetworkDriver):
        raise ScrapliCfgException(
            "provided scrapli connection is sync but using 'AsyncScrapliCfg' -- you must use an "
            "async connection with 'AsyncScrapliCfg'!"
        )

    platform_class = ASYNC_CORE_PLATFORM_MAP.get(type(conn))
    if not platform_class:
        raise ScrapliCfgException(
            f"scrapli connection object type '{type(conn)}' not a supported scrapli-cfg type"
        )

    final_platform: "AsyncScrapliCfgPlatform" = platform_class(
        conn=conn,
        config_sources=config_sources,
        on_prepare=on_prepare,
        dedicated_connection=dedicated_connection,
        ignore_version=ignore_version,
        **kwargs,
    )

    return final_platform
        </code>
    </pre>
</details>



## Functions

    

#### AsyncScrapliCfg
`AsyncScrapliCfg(conn: scrapli.driver.network.async_driver.AsyncNetworkDriver, *, config_sources: Optional[List[str]] = None, on_prepare: Optional[Callable[..., Any]] = None, dedicated_connection: bool = False, ignore_version: bool = False, **kwargs: Any) ‑> AsyncScrapliCfgPlatform`

```text
Scrapli Config Async Factory

Return a async scrapli config object for the provided platform. Prefer to use factory classes
just so that the naming convention (w/ upper case things) is "right", but given that the class
version inherited from the base ScrapliCfgPlatform and did not implement the abstract methods
this felt like a better move.

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
    kwargs: keyword args to pass to the scrapli_cfg object (for things like iosxe 'filesystem'
        argument)

Returns:
    AsyncScrapliCfg: async scrapli cfg object

Raises:
    ScrapliCfgException: if provided connection object is sync
    ScrapliCfgException: if provided connection object is async but is not a supported ("core")
        platform type
```




    

#### ScrapliCfg
`ScrapliCfg(conn: scrapli.driver.network.sync_driver.NetworkDriver, *, config_sources: Optional[List[str]] = None, on_prepare: Optional[Callable[..., Any]] = None, dedicated_connection: bool = False, ignore_version: bool = False, **kwargs: Any) ‑> ScrapliCfgPlatform`

```text
Scrapli Config Sync Factory

Return a sync scrapli config object for the provided platform. Prefer to use factory classes
just so that the naming convention (w/ upper case things) is "right", but given that the class
version inherited from the base ScrapliCfgPlatform and did not implement the abstract methods
this felt like a better move.

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
    kwargs: keyword args to pass to the scrapli_cfg object (for things like iosxe 'filesystem'
        argument)

Returns:
    ScrapliCfg: sync scrapli cfg object

Raises:
    ScrapliCfgException: if provided connection object is async
    ScrapliCfgException: if provided connection object is sync but is not a supported ("core")
        platform type
```