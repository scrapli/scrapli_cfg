<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.platform.core.juniper_junos.patterns

scrapli_cfg.platform.core.juniper_junos.patterns

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_cfg.platform.core.juniper_junos.patterns"""
import re

VERSION_PATTERN = re.compile(
    # should match at least versions looking like:
    # 17.3R2.10
    # 18.1R3-S2.5
    pattern=r"\d+\.[\w-]+\.\w+",
)
OUTPUT_HEADER_PATTERN = re.compile(pattern=r"^## last commit.*$\nversion.*$", flags=re.M | re.I)
EDIT_PATTERN = re.compile(pattern=r"^\[edit\]$", flags=re.M)
        </code>
    </pre>
</details>