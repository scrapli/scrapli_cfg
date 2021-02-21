"""scrapli_cfg.platform.core.cisco_iosxe.types"""
from enum import Enum


class FilePromptMode(Enum):
    """Enum representing file prompt modes"""

    NOISY = "noisy"
    ALERT = "alert"
    QUIET = "quiet"
