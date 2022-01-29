"""scrapli_cfg.helper"""


def strip_blank_lines(config: str) -> str:
    """
    Strip blank lines out of a config

    Args:
        config: config to normalize

    Returns:
        str: normalized config

    Raises:
        N/A

    """
    return "\n".join(line for line in config.splitlines() if line)
