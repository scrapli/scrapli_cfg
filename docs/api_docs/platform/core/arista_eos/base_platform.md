<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.platform.core.arista_eos.base_platform

scrapli_cfg.platform.core.arista_eos.base

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_cfg.platform.core.arista_eos.base"""
import re
from datetime import datetime
from logging import LoggerAdapter
from typing import List, Tuple

from scrapli_cfg.platform.core.arista_eos.patterns import (
    BANNER_PATTERN,
    END_PATTERN,
    GLOBAL_COMMENT_LINE_PATTERN,
)

CONFIG_SOURCES = [
    "running",
    "startup",
]


class ScrapliCfgEOSBase:
    logger: LoggerAdapter
    config_sources: List[str]
    config_session_name: str
    candidate_config: str

    @staticmethod
    def _get_config_command(source: str) -> str:
        """
        Handle pre "get_config" operations for parity between sync and async

        Args:
            source: name of the config source, generally running|startup

        Returns:
            str: command to use to fetch the requested config

        Raises:
            InvalidConfigTarget: if the requested config source is not valid

        """
        if source == "running":
            return "show running-config"
        return "show startup-config"

    @staticmethod
    def _prepare_config_payloads(config: str) -> Tuple[str, str]:
        """
        Prepare a configuration so it can be nicely sent to the device via scrapli

        Args:
            config: configuration to prep

        Returns:
            tuple: tuple of "normal" config lines and "eager" config lines

        Raises:
            N/A

        """
        # remove comment lines
        config = re.sub(pattern=GLOBAL_COMMENT_LINE_PATTERN, repl="!", string=config)

        # remove "end" at the end of config if present - if its present it will drop scrapli out
        # of the config session which we do not want
        config = re.sub(pattern=END_PATTERN, repl="!", string=config)

        # find all sections that need to be "eagerly" sent
        eager_config = re.findall(pattern=BANNER_PATTERN, string=config)
        for eager_section in eager_config:
            config = config.replace(eager_section, "!")

        joined_eager_config = "\n".join(eager_config)

        return config, joined_eager_config

    def _prepare_load_config_session_and_payload(self, config: str) -> Tuple[str, str, bool]:
        """
        Handle pre "load_config" operations for parity between sync and async

        Args:
            config: candidate config to load

        Returns:
            tuple: tuple containing "normal" config elements to send to the device and "eager" mode
                config elements to send to the device (things like banners/macro that require
                scrapli "eager=True"), and lastly a bool indicating if the config session needs to
                be registered on the device

        Raises:
            N/A

        """
        config, eager_config = self._prepare_config_payloads(config=config)

        register_config_session = False
        if not self.config_session_name:
            self.config_session_name = f"scrapli_cfg_{round(datetime.now().timestamp())}"
            self.logger.debug(f"configuration session name will be '{self.config_session_name}'")
            register_config_session = True

        return config, eager_config, register_config_session

    def _reset_config_session(self) -> None:
        """
        Reset config session info

        Resets the candidate config and config session name attributes -- when these are "empty" we
        know there is no current config session

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self.logger.debug("resetting candidate config and config session name")
        self.candidate_config = ""
        self.config_session_name = ""

    def _normalize_source_candidate_configs(self, source_config: str) -> Tuple[str, str]:
        """
        Handle post "diff_config" operations for parity between sync and async

        Args:
            source_config: current config of the source config store

        Returns:
            ScrapliCfgDiff: scrapli cfg diff object

        Raises:
            N/A

        """
        self.logger.debug("normalizing source and candidate configs for diff object")

        # Remove all comment lines from both the source and candidate configs -- this is only done
        # here pre-diff, so we dont modify the user provided candidate config which can totally have
        # those comment lines - we only remove "global" (top level) comments though... user comments
        # attached to interfaces and the stuff will remain
        source_config = re.sub(pattern=GLOBAL_COMMENT_LINE_PATTERN, string=source_config, repl="")
        source_config = "\n".join(line for line in source_config.splitlines() if line)
        candidate_config = re.sub(
            pattern=GLOBAL_COMMENT_LINE_PATTERN, string=self.candidate_config, repl=""
        )
        candidate_config = "\n".join(line for line in candidate_config.splitlines() if line)

        return source_config, candidate_config
        </code>
    </pre>
</details>




## Classes

### ScrapliCfgEOSBase



<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class ScrapliCfgEOSBase:
    logger: LoggerAdapter
    config_sources: List[str]
    config_session_name: str
    candidate_config: str

    @staticmethod
    def _get_config_command(source: str) -> str:
        """
        Handle pre "get_config" operations for parity between sync and async

        Args:
            source: name of the config source, generally running|startup

        Returns:
            str: command to use to fetch the requested config

        Raises:
            InvalidConfigTarget: if the requested config source is not valid

        """
        if source == "running":
            return "show running-config"
        return "show startup-config"

    @staticmethod
    def _prepare_config_payloads(config: str) -> Tuple[str, str]:
        """
        Prepare a configuration so it can be nicely sent to the device via scrapli

        Args:
            config: configuration to prep

        Returns:
            tuple: tuple of "normal" config lines and "eager" config lines

        Raises:
            N/A

        """
        # remove comment lines
        config = re.sub(pattern=GLOBAL_COMMENT_LINE_PATTERN, repl="!", string=config)

        # remove "end" at the end of config if present - if its present it will drop scrapli out
        # of the config session which we do not want
        config = re.sub(pattern=END_PATTERN, repl="!", string=config)

        # find all sections that need to be "eagerly" sent
        eager_config = re.findall(pattern=BANNER_PATTERN, string=config)
        for eager_section in eager_config:
            config = config.replace(eager_section, "!")

        joined_eager_config = "\n".join(eager_config)

        return config, joined_eager_config

    def _prepare_load_config_session_and_payload(self, config: str) -> Tuple[str, str, bool]:
        """
        Handle pre "load_config" operations for parity between sync and async

        Args:
            config: candidate config to load

        Returns:
            tuple: tuple containing "normal" config elements to send to the device and "eager" mode
                config elements to send to the device (things like banners/macro that require
                scrapli "eager=True"), and lastly a bool indicating if the config session needs to
                be registered on the device

        Raises:
            N/A

        """
        config, eager_config = self._prepare_config_payloads(config=config)

        register_config_session = False
        if not self.config_session_name:
            self.config_session_name = f"scrapli_cfg_{round(datetime.now().timestamp())}"
            self.logger.debug(f"configuration session name will be '{self.config_session_name}'")
            register_config_session = True

        return config, eager_config, register_config_session

    def _reset_config_session(self) -> None:
        """
        Reset config session info

        Resets the candidate config and config session name attributes -- when these are "empty" we
        know there is no current config session

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self.logger.debug("resetting candidate config and config session name")
        self.candidate_config = ""
        self.config_session_name = ""

    def _normalize_source_candidate_configs(self, source_config: str) -> Tuple[str, str]:
        """
        Handle post "diff_config" operations for parity between sync and async

        Args:
            source_config: current config of the source config store

        Returns:
            ScrapliCfgDiff: scrapli cfg diff object

        Raises:
            N/A

        """
        self.logger.debug("normalizing source and candidate configs for diff object")

        # Remove all comment lines from both the source and candidate configs -- this is only done
        # here pre-diff, so we dont modify the user provided candidate config which can totally have
        # those comment lines - we only remove "global" (top level) comments though... user comments
        # attached to interfaces and the stuff will remain
        source_config = re.sub(pattern=GLOBAL_COMMENT_LINE_PATTERN, string=source_config, repl="")
        source_config = "\n".join(line for line in source_config.splitlines() if line)
        candidate_config = re.sub(
            pattern=GLOBAL_COMMENT_LINE_PATTERN, string=self.candidate_config, repl=""
        )
        candidate_config = "\n".join(line for line in candidate_config.splitlines() if line)

        return source_config, candidate_config
        </code>
    </pre>
</details>


#### Descendants
- scrapli_cfg.platform.core.arista_eos.async_platform.AsyncScrapliCfgEOS
- scrapli_cfg.platform.core.arista_eos.sync_platform.ScrapliCfgEOS
#### Class variables

    
`candidate_config: str`




    
`config_session_name: str`




    
`config_sources: List[str]`




    
`logger: logging.LoggerAdapter`