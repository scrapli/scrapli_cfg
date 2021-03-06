from scrapli.driver.core import (
    AsyncEOSDriver,
    AsyncIOSXEDriver,
    AsyncIOSXRDriver,
    AsyncNXOSDriver,
    EOSDriver,
    IOSXEDriver,
    IOSXRDriver,
    NXOSDriver,
)
from scrapli_cfg import AsyncScrapliCfg, ScrapliCfg
from scrapli_cfg.platform.core.arista_eos import AsyncScrapliCfgEOS, ScrapliCfgEOS
from scrapli_cfg.platform.core.cisco_iosxe import AsyncScrapliCfgIOSXE, ScrapliCfgIOSXE
from scrapli_cfg.platform.core.cisco_iosxr import AsyncScrapliCfgIOSXR, ScrapliCfgIOSXR
from scrapli_cfg.platform.core.cisco_nxos import AsyncScrapliCfgNXOS, ScrapliCfgNXOS

ASYNC_CORE_PLATFORM_MAP = {
    AsyncEOSDriver: AsyncScrapliCfgEOS,
    AsyncIOSXEDriver: AsyncScrapliCfgIOSXE,
    AsyncIOSXRDriver: AsyncScrapliCfgIOSXR,
    AsyncNXOSDriver: AsyncScrapliCfgNXOS,
}
SYNC_CORE_PLATFORM_MAP = {
    EOSDriver: ScrapliCfgEOS,
    IOSXEDriver: ScrapliCfgIOSXE,
    IOSXRDriver: ScrapliCfgIOSXR,
    NXOSDriver: ScrapliCfgNXOS,
}


def test_sync_factory(sync_scrapli_conn):
    scrapli_cfg_obj = ScrapliCfg(conn=sync_scrapli_conn)
    assert isinstance(scrapli_cfg_obj, SYNC_CORE_PLATFORM_MAP.get(type(sync_scrapli_conn)))


def test_async_factory(async_scrapli_conn):
    scrapli_cfg_obj = AsyncScrapliCfg(conn=async_scrapli_conn)
    assert isinstance(scrapli_cfg_obj, ASYNC_CORE_PLATFORM_MAP.get(type(async_scrapli_conn)))
