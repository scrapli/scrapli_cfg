<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.platform.core.cisco_iosxe.base_platform

scrapli_cfg.platform.core.cisco_iosxe.base

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_cfg.platform.core.cisco_iosxe.base"""
import re
from datetime import datetime
from enum import Enum
from logging import Logger, LoggerAdapter
from typing import TYPE_CHECKING, Tuple

from scrapli_cfg.exceptions import FailedToFetchSpaceAvailable, InsufficientSpaceAvailable
from scrapli_cfg.helper import strip_blank_lines
from scrapli_cfg.platform.core.cisco_iosxe.patterns import (
    BYTES_FREE,
    FILE_PROMPT_MODE,
    OUTPUT_HEADER_PATTERN,
    VERSION_PATTERN,
)

if TYPE_CHECKING:
    LoggerAdapterT = LoggerAdapter[Logger]  # pylint:disable=E1136
else:
    LoggerAdapterT = LoggerAdapter


CONFIG_SOURCES = [
    "running",
    "startup",
]


class FilePromptMode(Enum):
    """Enum representing file prompt modes"""

    NOISY = "noisy"
    ALERT = "alert"
    QUIET = "quiet"


class ScrapliCfgIOSXEBase:
    logger: LoggerAdapterT
    candidate_config: str
    candidate_config_filename: str
    _replace: bool
    filesystem: str
    _filesystem_space_available_buffer_perc: int

    def _post_get_filesystem_space_available(self, output: str) -> int:
        """
        Handle post "get_filesystem_space_available" operations for parity between sync and async

        Args:
            output: output that was fetched from the device

        Returns:
            int: bytes of space available on filesystem

        Raises:
            FailedToFetchSpaceAvailable: if could not determine space available... duh :)

        """
        self.logger.info("determining space available from device output")

        bytes_available_match = re.search(pattern=BYTES_FREE, string=output)
        if not bytes_available_match:
            msg = "could not determine space available on filesystem"
            self.logger.critical(msg)
            raise FailedToFetchSpaceAvailable(msg)

        return int(bytes_available_match.groupdict()["bytes_available"])

    def _space_available(self, filesystem_bytes_available: int) -> None:
        """
        Space available operations for parity between sync and async

        It seems that on iosxe the length of the config is near enough 1:1 to the size it takes up
        on the disk... so roll w/ that plus a bit of buffer based on the available buffer perc

        Args:
            filesystem_bytes_available: bytes available on filesystem

        Returns:
            None

        Raises:
            InsufficientSpaceAvailable: if... insufficient space available....

        """
        if filesystem_bytes_available < (
            len(self.candidate_config) / (self._filesystem_space_available_buffer_perc / 100)
        ) + len(self.candidate_config):
            # filesystem has less than candidate config file size + 10% (by default) space, bail out
            msg = (
                f"insufficient space available for candidate config + "
                f"{self._filesystem_space_available_buffer_perc}% (buffer)"
            )
            self.logger.critical(msg)
            raise InsufficientSpaceAvailable(msg)

    def _post_determine_file_prompt_mode(self, output: str) -> FilePromptMode:
        """
        Handle post "determine_file_prompt_mode" operations for parity between sync and async

        Args:
            output: output that was fetched from the device

        Returns:
            FilePromptMode: enum representing file prompt mode

        Raises:
            N/A

        """
        self.logger.debug("determining file prompt mode from device output")

        file_prompt_match = re.search(pattern=FILE_PROMPT_MODE, string=output)
        if not file_prompt_match:
            return FilePromptMode.ALERT
        prompt_mode = file_prompt_match.groupdict()["prompt_mode"]
        if prompt_mode == "noisy":
            return FilePromptMode.NOISY
        return FilePromptMode.QUIET

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

    def clean_config(self, config: str) -> str:
        """
        Clean a configuration file of unwanted lines

        Args:
            config: configuration string to "clean"; cleaning removes lines that would prevent using
                the provided configuration as a "load_config" source from working -- i.e. removes
                the leading "Building Configuration" line

        Returns:
            str: cleaned configuration string

        Raises:
            N/A

        """
        self.logger.debug("cleaning config file")

        return strip_blank_lines(
            config=re.sub(pattern=OUTPUT_HEADER_PATTERN, string=config, repl="")
        )

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

    @staticmethod
    def _get_config_command(source: str) -> str:
        """
        Return command to use to get config based on the provided source

        Args:
            source: name of the config source, generally running|startup

        Returns:
            str: command to use to fetch the requested config

        Raises:
            N/A

        """
        if source == "running":
            return "show running-config"
        return "show startup-config"

    def _get_diff_command(self, source: str) -> str:
        """
        Return command to use to get config diff based on the provided source

        Args:
            source: name of the config source, generally running|startup

        Returns:
            str: command to use to fetch the requested config

        Raises:
            N/A

        """
        if self._replace:
            return (
                f"show archive config differences system:{source}-config {self.filesystem}"
                f"{self.candidate_config_filename}"
            )
        return (
            f"show archive config incremental-diffs {self.filesystem}"
            f"{self.candidate_config_filename} ignorecase"
        )

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
        tclsh_start_file = f'puts [open "{self.filesystem}{self.candidate_config_filename}" w+] {{'
        tclsh_end_file = "}"
        final_config = "\n".join((tclsh_start_file, config, tclsh_end_file))

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

        # remove any of the leading timestamp/building config/config size/last change lines in
        # both the source and candidate configs so they dont need to be compared
        source_config = self.clean_config(config=source_config)
        candidate_config = self.clean_config(config=self.candidate_config)

        return source_config, candidate_config
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






### ScrapliCfgIOSXEBase



<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class ScrapliCfgIOSXEBase:
    logger: LoggerAdapterT
    candidate_config: str
    candidate_config_filename: str
    _replace: bool
    filesystem: str
    _filesystem_space_available_buffer_perc: int

    def _post_get_filesystem_space_available(self, output: str) -> int:
        """
        Handle post "get_filesystem_space_available" operations for parity between sync and async

        Args:
            output: output that was fetched from the device

        Returns:
            int: bytes of space available on filesystem

        Raises:
            FailedToFetchSpaceAvailable: if could not determine space available... duh :)

        """
        self.logger.info("determining space available from device output")

        bytes_available_match = re.search(pattern=BYTES_FREE, string=output)
        if not bytes_available_match:
            msg = "could not determine space available on filesystem"
            self.logger.critical(msg)
            raise FailedToFetchSpaceAvailable(msg)

        return int(bytes_available_match.groupdict()["bytes_available"])

    def _space_available(self, filesystem_bytes_available: int) -> None:
        """
        Space available operations for parity between sync and async

        It seems that on iosxe the length of the config is near enough 1:1 to the size it takes up
        on the disk... so roll w/ that plus a bit of buffer based on the available buffer perc

        Args:
            filesystem_bytes_available: bytes available on filesystem

        Returns:
            None

        Raises:
            InsufficientSpaceAvailable: if... insufficient space available....

        """
        if filesystem_bytes_available < (
            len(self.candidate_config) / (self._filesystem_space_available_buffer_perc / 100)
        ) + len(self.candidate_config):
            # filesystem has less than candidate config file size + 10% (by default) space, bail out
            msg = (
                f"insufficient space available for candidate config + "
                f"{self._filesystem_space_available_buffer_perc}% (buffer)"
            )
            self.logger.critical(msg)
            raise InsufficientSpaceAvailable(msg)

    def _post_determine_file_prompt_mode(self, output: str) -> FilePromptMode:
        """
        Handle post "determine_file_prompt_mode" operations for parity between sync and async

        Args:
            output: output that was fetched from the device

        Returns:
            FilePromptMode: enum representing file prompt mode

        Raises:
            N/A

        """
        self.logger.debug("determining file prompt mode from device output")

        file_prompt_match = re.search(pattern=FILE_PROMPT_MODE, string=output)
        if not file_prompt_match:
            return FilePromptMode.ALERT
        prompt_mode = file_prompt_match.groupdict()["prompt_mode"]
        if prompt_mode == "noisy":
            return FilePromptMode.NOISY
        return FilePromptMode.QUIET

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

    def clean_config(self, config: str) -> str:
        """
        Clean a configuration file of unwanted lines

        Args:
            config: configuration string to "clean"; cleaning removes lines that would prevent using
                the provided configuration as a "load_config" source from working -- i.e. removes
                the leading "Building Configuration" line

        Returns:
            str: cleaned configuration string

        Raises:
            N/A

        """
        self.logger.debug("cleaning config file")

        return strip_blank_lines(
            config=re.sub(pattern=OUTPUT_HEADER_PATTERN, string=config, repl="")
        )

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

    @staticmethod
    def _get_config_command(source: str) -> str:
        """
        Return command to use to get config based on the provided source

        Args:
            source: name of the config source, generally running|startup

        Returns:
            str: command to use to fetch the requested config

        Raises:
            N/A

        """
        if source == "running":
            return "show running-config"
        return "show startup-config"

    def _get_diff_command(self, source: str) -> str:
        """
        Return command to use to get config diff based on the provided source

        Args:
            source: name of the config source, generally running|startup

        Returns:
            str: command to use to fetch the requested config

        Raises:
            N/A

        """
        if self._replace:
            return (
                f"show archive config differences system:{source}-config {self.filesystem}"
                f"{self.candidate_config_filename}"
            )
        return (
            f"show archive config incremental-diffs {self.filesystem}"
            f"{self.candidate_config_filename} ignorecase"
        )

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
        tclsh_start_file = f'puts [open "{self.filesystem}{self.candidate_config_filename}" w+] {{'
        tclsh_end_file = "}"
        final_config = "\n".join((tclsh_start_file, config, tclsh_end_file))

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

        # remove any of the leading timestamp/building config/config size/last change lines in
        # both the source and candidate configs so they dont need to be compared
        source_config = self.clean_config(config=source_config)
        candidate_config = self.clean_config(config=self.candidate_config)

        return source_config, candidate_config
        </code>
    </pre>
</details>


#### Descendants
- scrapli_cfg.platform.core.cisco_iosxe.async_platform.AsyncScrapliCfgIOSXE
- scrapli_cfg.platform.core.cisco_iosxe.sync_platform.ScrapliCfgIOSXE
#### Class variables

    
`candidate_config: str`




    
`candidate_config_filename: str`




    
`filesystem: str`




    
`logger: logging.LoggerAdapter`



#### Methods

    

##### clean_config
`clean_config(self, config: str) ‑> str`

```text
Clean a configuration file of unwanted lines

Args:
    config: configuration string to "clean"; cleaning removes lines that would prevent using
        the provided configuration as a "load_config" source from working -- i.e. removes
        the leading "Building Configuration" line

Returns:
    str: cleaned configuration string

Raises:
    N/A
```