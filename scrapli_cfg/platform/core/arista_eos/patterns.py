"""scrapli_cfg.platform.core.arista_eos.patterns"""

import re

VERSION_PATTERN = re.compile(pattern=r"\d+\.\d+\.[a-z0-9\-]+(\.\d+[a-z]{0,1})?", flags=re.I)
GLOBAL_COMMENT_LINE_PATTERN = re.compile(pattern=r"^\! .*$", flags=re.I | re.M)
BANNER_PATTERN = re.compile(pattern=r"^banner.*EOF$", flags=re.I | re.M | re.S)
END_PATTERN = re.compile(pattern="end$")

# pre-canned config section grabber patterns

# match all ethernet interfaces w/ or w/out config items below them
ETHERNET_INTERFACES = re.compile(
    pattern=r"(^interface ethernet\d+$(?:\n^\s{3}.*$)*\n!\n)+", flags=re.I | re.M
)
# match management1 interface and config items below it
MANAGEMENT_ONE_INTERFACE = re.compile(
    pattern=r"^interface management1$(?:\n^\s{3}.*$)*\n!", flags=re.I | re.M
)
