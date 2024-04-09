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
