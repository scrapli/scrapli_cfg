import logging
from pathlib import Path

from scrapli_cfg.logging import ScrapliFileHandler, ScrapliFormatter, enable_basic_logging, logger


def test_enable_basic_logging(fs):
    assert Path("scrapli_cfg.log").is_file() is False
    enable_basic_logging(file=True, level="debug")
    scrapli_logger = logging.getLogger("scrapli_cfg")

    assert scrapli_logger.level == 10
    assert isinstance(scrapli_logger.handlers[1], ScrapliFileHandler)
    assert isinstance(scrapli_logger.handlers[1].formatter, ScrapliFormatter)
    assert scrapli_logger.propagate is False

    assert Path("scrapli_cfg.log").is_file() is True

    # reset the main logger to propagate and delete the file handler so caplog works!
    logger.propagate = True
    del logger.handlers[1]


def test_enable_basic_logging_no_buffer(fs):
    assert Path("mylog.log").is_file() is False

    enable_basic_logging(file="mylog.log", level="debug", buffer_log=False, caller_info=True)
    scrapli_logger = logging.getLogger("scrapli_cfg")

    assert scrapli_logger.level == 10
    assert isinstance(scrapli_logger.handlers[1], logging.FileHandler)
    assert isinstance(scrapli_logger.handlers[1].formatter, ScrapliFormatter)
    assert scrapli_logger.propagate is False

    assert Path("mylog.log").is_file() is True

    # reset the main logger to propagate and delete the file handler so caplog works!
    logger.propagate = True
    del logger.handlers[1]
