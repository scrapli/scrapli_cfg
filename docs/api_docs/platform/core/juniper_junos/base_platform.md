<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.platform.core.juniper_junos.base_platform

scrapli_cfg.platform.core.juniper_junos.base_platform

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_cfg.platform.core.juniper_junos.base_platform"""
import re
from datetime import datetime
from logging import LoggerAdapter
from typing import Tuple

from scrapli_cfg.platform.core.juniper_junos.patterns import (
    EDIT_PATTERN,
    OUTPUT_HEADER_PATTERN,
    VERSION_PATTERN,
)

CONFIG_SOURCES = [
    "running",
]


class ScrapliCfgJunosBase:
    logger: LoggerAdapter
    candidate_config: str
    candidate_config_filename: str
    _in_configuration_session: bool
    _replace: bool
    _set: bool
    filesystem: str

    @staticmethod
    def _parse_version(device_output: str) -> str:
        """
        Parse version string out of device output

        Args:
            device_output: output from show version command

        Returns:
            str: device version string

        Raises:
            N/A

        """
        version_string_search = re.search(pattern=VERSION_PATTERN, string=device_output)

        if not version_string_search:
            return ""

        version_string = version_string_search.group(0) or ""
        return version_string

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
        self.logger.debug("resetting candidate config and candidate config file name")
        self.candidate_config = ""
        self.candidate_config_filename = ""
        self._in_configuration_session = False
        self._set = False

    def _prepare_config_payloads(self, config: str) -> str:
        """
        Prepare a configuration so it can be nicely sent to the device via scrapli

        Args:
            config: configuration to prep

        Returns:
            str: string of config lines to write to candidate config file

        Raises:
            N/A

        """
        final_config_list = []
        for config_line in config.splitlines():
            final_config_list.append(
                f"echo >> {self.filesystem}{self.candidate_config_filename} '{config_line}'"
            )

        final_config = "\n".join(final_config_list)

        return final_config

    def _prepare_load_config(self, config: str, replace: bool) -> str:
        """
        Handle pre "load_config" operations for parity between sync and async

        Args:
            config: candidate config to load
            replace: True/False replace the configuration; passed here so it can be set at the class
                level as we need to stay in config mode and we need to know if we are doing a merge
                or a replace when we go to diff things

        Returns:
            str: string of config to write to candidate config file

        Raises:
            N/A

        """
        self.candidate_config = config

        if not self.candidate_config_filename:
            self.candidate_config_filename = f"scrapli_cfg_{round(datetime.now().timestamp())}"
            self.logger.debug(
                f"candidate config file name will be '{self.candidate_config_filename}'"
            )

        config = self._prepare_config_payloads(config=config)
        self._replace = replace

        return config

    def _normalize_source_candidate_configs(self, source_config: str) -> Tuple[str, str]:
        """
        Normalize candidate config and source config so that we can easily diff them

        Args:
            source_config: current config of the source config store

        Returns:
            ScrapliCfgDiff: scrapli cfg diff object

        Raises:
            N/A

        """
        self.logger.debug("normalizing source and candidate configs for diff object")

        source_config = re.sub(pattern=OUTPUT_HEADER_PATTERN, string=source_config, repl="")
        source_config = re.sub(pattern=EDIT_PATTERN, string=source_config, repl="")
        source_config = "\n".join(line for line in source_config.splitlines() if line)
        candidate_config = re.sub(
            pattern=OUTPUT_HEADER_PATTERN, string=self.candidate_config, repl=""
        )
        candidate_config = "\n".join(line for line in candidate_config.splitlines() if line)

        return source_config, candidate_config
        </code>
    </pre>
</details>




## Classes

### ScrapliCfgJunosBase



<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class ScrapliCfgJunosBase:
    logger: LoggerAdapter
    candidate_config: str
    candidate_config_filename: str
    _in_configuration_session: bool
    _replace: bool
    _set: bool
    filesystem: str

    @staticmethod
    def _parse_version(device_output: str) -> str:
        """
        Parse version string out of device output

        Args:
            device_output: output from show version command

        Returns:
            str: device version string

        Raises:
            N/A

        """
        version_string_search = re.search(pattern=VERSION_PATTERN, string=device_output)

        if not version_string_search:
            return ""

        version_string = version_string_search.group(0) or ""
        return version_string

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
        self.logger.debug("resetting candidate config and candidate config file name")
        self.candidate_config = ""
        self.candidate_config_filename = ""
        self._in_configuration_session = False
        self._set = False

    def _prepare_config_payloads(self, config: str) -> str:
        """
        Prepare a configuration so it can be nicely sent to the device via scrapli

        Args:
            config: configuration to prep

        Returns:
            str: string of config lines to write to candidate config file

        Raises:
            N/A

        """
        final_config_list = []
        for config_line in config.splitlines():
            final_config_list.append(
                f"echo >> {self.filesystem}{self.candidate_config_filename} '{config_line}'"
            )

        final_config = "\n".join(final_config_list)

        return final_config

    def _prepare_load_config(self, config: str, replace: bool) -> str:
        """
        Handle pre "load_config" operations for parity between sync and async

        Args:
            config: candidate config to load
            replace: True/False replace the configuration; passed here so it can be set at the class
                level as we need to stay in config mode and we need to know if we are doing a merge
                or a replace when we go to diff things

        Returns:
            str: string of config to write to candidate config file

        Raises:
            N/A

        """
        self.candidate_config = config

        if not self.candidate_config_filename:
            self.candidate_config_filename = f"scrapli_cfg_{round(datetime.now().timestamp())}"
            self.logger.debug(
                f"candidate config file name will be '{self.candidate_config_filename}'"
            )

        config = self._prepare_config_payloads(config=config)
        self._replace = replace

        return config

    def _normalize_source_candidate_configs(self, source_config: str) -> Tuple[str, str]:
        """
        Normalize candidate config and source config so that we can easily diff them

        Args:
            source_config: current config of the source config store

        Returns:
            ScrapliCfgDiff: scrapli cfg diff object

        Raises:
            N/A

        """
        self.logger.debug("normalizing source and candidate configs for diff object")

        source_config = re.sub(pattern=OUTPUT_HEADER_PATTERN, string=source_config, repl="")
        source_config = re.sub(pattern=EDIT_PATTERN, string=source_config, repl="")
        source_config = "\n".join(line for line in source_config.splitlines() if line)
        candidate_config = re.sub(
            pattern=OUTPUT_HEADER_PATTERN, string=self.candidate_config, repl=""
        )
        candidate_config = "\n".join(line for line in candidate_config.splitlines() if line)

        return source_config, candidate_config
        </code>
    </pre>
</details>


#### Descendants
- scrapli_cfg.platform.core.juniper_junos.async_platform.AsyncScrapliCfgJunos
- scrapli_cfg.platform.core.juniper_junos.sync_platform.ScrapliCfgJunos
#### Class variables

    
`candidate_config: str`




    
`candidate_config_filename: str`




    
`filesystem: str`




    
`logger: logging.LoggerAdapter`