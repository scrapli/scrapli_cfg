<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.platform.core.cisco_iosxr.patterns

scrapli_cfg.platform.core.cisco_iosxr.patterns

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_cfg.platform.core.cisco_iosxr.patterns"""
import re

VERSION_PATTERN = re.compile(pattern=r"\d+\.\d+\.\d+", flags=re.I)
BANNER_PATTERN = re.compile(
    pattern=r"^banner\s(?:(exec|incoming|login|motd|prompt-timeout|slip-ppp)\s)"
    r"(?P<delim>.{1}).*\?P=delim",
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
ETHERNET_INTERFACES = re.compile(
    pattern=r"(^interface \w+ethernet(?:\d|\/)+$(?:\n^\s{1}.*$)*\n!\n)+", flags=re.I | re.M
)
# match mgmteth[numbers, letters, forward slashes] interface and config items below it
MANAGEMENT_ONE_INTERFACE = re.compile(
    pattern=r"^^interface mgmteth(?:[a-z0-9\/]+)(?:\n^\s.*$)*\n!", flags=re.I | re.M
)
        </code>
    </pre>
</details>