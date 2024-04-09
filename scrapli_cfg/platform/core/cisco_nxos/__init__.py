"""scrapli_cfg.platform.core.cisco_nxos"""

from scrapli_cfg.platform.core.cisco_nxos.async_platform import AsyncScrapliCfgNXOS
from scrapli_cfg.platform.core.cisco_nxos.sync_platform import ScrapliCfgNXOS

__all__ = (
    "AsyncScrapliCfgNXOS",
    "ScrapliCfgNXOS",
)
