<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.platform.core.arista_eos.patterns

scrapli_cfg.platform.core.arista_eos.patterns

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_cfg.platform.core.arista_eos.patterns"""
import re

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
        </code>
    </pre>
</details>