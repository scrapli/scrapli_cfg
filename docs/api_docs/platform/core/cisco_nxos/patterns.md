<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.platform.core.cisco_nxos.patterns

scrapli_cfg.platforms.cisco_nxos.patterns

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
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
        </code>
    </pre>
</details>