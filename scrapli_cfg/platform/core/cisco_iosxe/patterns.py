"""scrapli_cfg.platform.core.cisco_iosxe.patterns"""

import re

VERSION_PATTERN = re.compile(pattern=r"\d+\.[a-z0-9\(\)\.]+", flags=re.I)
BYTES_FREE = re.compile(pattern=r"(?P<bytes_available>\d+)(?: bytes free)", flags=re.I)
FILE_PROMPT_MODE = re.compile(pattern=r"(?:file prompt )(?P<prompt_mode>\w+)", flags=re.I)

OUTPUT_HEADER_PATTERN = re.compile(
    pattern=r".*(?=(version \d+\.\d+))",
    flags=re.I | re.S,
)
