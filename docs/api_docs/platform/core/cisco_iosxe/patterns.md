<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.platform.core.cisco_iosxe.patterns

scrapli_cfg.platform.core.cisco_iosxe.patterns

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_cfg.platform.core.cisco_iosxe.patterns"""
import re

VERSION_PATTERN = re.compile(pattern=r"\d+\.[a-z0-9\(\)\.]+", flags=re.I)
BYTES_FREE = re.compile(pattern=r"(?P<bytes_available>\d+)(?: bytes free)", flags=re.I)
FILE_PROMPT_MODE = re.compile(pattern=r"(?:file prompt )(?P<prompt_mode>\w+)", flags=re.I)

OUTPUT_HEADER_PATTERN = re.compile(
    pattern=r".*(?=(version \d+\.\d+))",
    flags=re.I | re.S,
)
        </code>
    </pre>
</details>