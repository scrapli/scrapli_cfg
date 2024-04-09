"""scrapli_cfg.platform.core.cisco_iosxr.patterns"""

import re

VERSION_PATTERN = re.compile(pattern=r"\d+\.\d+\.\d+", flags=re.I)
BANNER_PATTERN = re.compile(
    pattern=r"(^banner\s(?:exec|incoming|login|motd|prompt-timeout|slip-ppp)\s"
    r"(?P<delim>.{1}).*(?P=delim)$)",
    flags=re.I | re.M | re.S,
)

TIMESTAMP_PATTERN = datetime_pattern = re.compile(
    r"^(mon|tue|wed|thu|fri|sat|sun)\s+"
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+"
    r"\d+\s+\d+:\d+:\d+((\.\d+\s\w+)|\s\d+)$",
    flags=re.M | re.I,
)
BUILD_CONFIG_PATTERN = re.compile(r"(^building configuration\.\.\.$)", flags=re.I | re.M)
CONFIG_VERSION_PATTERN = re.compile(r"(^!! ios xr.*$)", flags=re.I | re.M)
CONFIG_CHANGE_PATTERN = re.compile(r"(^!! last config.*$)", flags=re.I | re.M)
OUTPUT_HEADER_PATTERN = re.compile(
    pattern=rf"{TIMESTAMP_PATTERN.pattern}|"
    rf"{BUILD_CONFIG_PATTERN.pattern}|"
    rf"{CONFIG_VERSION_PATTERN.pattern}|"
    rf"{CONFIG_CHANGE_PATTERN.pattern}",
    flags=re.I | re.M,
)

END_PATTERN = re.compile(pattern="end$")

# pre-canned config section grabber patterns

# match all ethernet interfaces w/ or w/out config items below them
IOSXR_INTERFACES_PATTERN = r"(?:Ethernet|GigabitEthernet|TenGigE|HundredGigE)"
ETHERNET_INTERFACES = re.compile(
    pattern=rf"(^interface {IOSXR_INTERFACES_PATTERN}(?:\d|\/)+$(?:\n^\s{1}.*$)*\n!\n)+",
    flags=re.I | re.M,
)
# match mgmteth[numbers, letters, forward slashes] interface and config items below it
MANAGEMENT_ONE_INTERFACE = re.compile(
    pattern=r"^^interface mgmteth(?:[a-z0-9\/]+)(?:\n^\s.*$)*\n!", flags=re.I | re.M
)
