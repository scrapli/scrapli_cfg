<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.logging

scrapli_cfg.logging

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_cfg.logging"""
from logging import FileHandler, NullHandler, getLogger
from typing import Union

from scrapli.logging import ScrapliFileHandler, ScrapliFormatter


def enable_basic_logging(
    file: Union[str, bool] = False,
    level: str = "info",
    caller_info: bool = False,
    buffer_log: bool = True,
) -> None:
    """
    Enable opinionated logging for scrapli_cfg

    Uses scrapli "core" formatter/file handler

    Args:
        file: True to output to default log path ("scrapli.log"), otherwise string path to write log
            file to
        level: string name of logging level to use, i.e. "info", "debug", etc.
        caller_info: add info about module/function/line in the log entry
        buffer_log: buffer log read outputs

    Returns:
        None

    Raises:
        N/A

    """
    logger.propagate = False
    logger.setLevel(level=level.upper())

    scrapli_formatter = ScrapliFormatter(caller_info=caller_info)

    if file:
        if isinstance(file, bool):
            filename = "scrapli_cfg.log"
        else:
            filename = file

        if not buffer_log:
            fh = FileHandler(filename=filename, mode="w")
        else:
            fh = ScrapliFileHandler(filename=filename, mode="w")

        fh.setFormatter(scrapli_formatter)

        logger.addHandler(fh)


logger = getLogger("scrapli_cfg")
logger.addHandler(NullHandler())
        </code>
    </pre>
</details>



## Functions

    

#### enable_basic_logging
`enable_basic_logging(file: Union[str, bool] = False, level: str = 'info', caller_info: bool = False, buffer_log: bool = True) ‑> NoneType`

```text
Enable opinionated logging for scrapli_cfg

Uses scrapli "core" formatter/file handler

Args:
    file: True to output to default log path ("scrapli.log"), otherwise string path to write log
        file to
    level: string name of logging level to use, i.e. "info", "debug", etc.
    caller_info: add info about module/function/line in the log entry
    buffer_log: buffer log read outputs

Returns:
    None

Raises:
    N/A
```