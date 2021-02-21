<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.platform.core.cisco_iosxe.types

scrapli_cfg.platform.core.cisco_iosxe.types

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_cfg.platform.core.cisco_iosxe.types"""
from enum import Enum


class FilePromptMode(Enum):
    """Enum representing file prompt modes"""

    NOISY = "noisy"
    ALERT = "alert"
    QUIET = "quiet"
        </code>
    </pre>
</details>




## Classes

### FilePromptMode


```text
Enum representing file prompt modes
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class FilePromptMode(Enum):
    """Enum representing file prompt modes"""

    NOISY = "noisy"
    ALERT = "alert"
    QUIET = "quiet"
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- enum.Enum
#### Class variables

    
`ALERT`




    
`NOISY`




    
`QUIET`