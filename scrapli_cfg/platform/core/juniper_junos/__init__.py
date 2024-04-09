"""scrapli_cfg.platform.core.juniper_junos"""

from scrapli_cfg.platform.core.juniper_junos.async_platform import AsyncScrapliCfgJunos
from scrapli_cfg.platform.core.juniper_junos.sync_platform import ScrapliCfgJunos

__all__ = (
    "AsyncScrapliCfgJunos",
    "ScrapliCfgJunos",
)
