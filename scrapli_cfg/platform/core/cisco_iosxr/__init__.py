"""scrapli_cfg.platform.core.cisco_iosxr"""

from scrapli_cfg.platform.core.cisco_iosxr.async_platform import AsyncScrapliCfgIOSXR
from scrapli_cfg.platform.core.cisco_iosxr.sync_platform import ScrapliCfgIOSXR

__all__ = (
    "AsyncScrapliCfgIOSXR",
    "ScrapliCfgIOSXR",
)
