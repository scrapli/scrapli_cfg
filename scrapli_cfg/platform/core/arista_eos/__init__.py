"""scrapli_cfg.platform.core.arista_eos"""

from scrapli_cfg.platform.core.arista_eos.async_platform import AsyncScrapliCfgEOS
from scrapli_cfg.platform.core.arista_eos.sync_platform import ScrapliCfgEOS

__all__ = (
    "AsyncScrapliCfgEOS",
    "ScrapliCfgEOS",
)
