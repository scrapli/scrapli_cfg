"""scrapli_cfg.platforms.cisco_nxos.patterns"""

import re

VERSION_PATTERN = re.compile(pattern=r"\d+\.[a-z0-9\(\)\.]+", flags=re.I)
BYTES_FREE = re.compile(pattern=r"(?P<bytes_available>\d+)(?: bytes free)", flags=re.I)

BUILD_CONFIG_PATTERN = re.compile(r"(^!command:.*$)", flags=re.I | re.M)
CONFIG_VERSION_PATTERN = re.compile(r"(^!running configuration last done.*$)", flags=re.I | re.M)
CONFIG_CHANGE_PATTERN = re.compile(r"(^!time.*$)", flags=re.I | re.M)
OUTPUT_HEADER_PATTERN = re.compile(
    pattern=rf"{BUILD_CONFIG_PATTERN.pattern}|"
    rf"{CONFIG_VERSION_PATTERN.pattern}|"
    rf"{CONFIG_CHANGE_PATTERN.pattern}",
    flags=re.I | re.M,
)

CHECKPOINT_LINE = re.compile(pattern=r"^\s*!#.*$", flags=re.M)
