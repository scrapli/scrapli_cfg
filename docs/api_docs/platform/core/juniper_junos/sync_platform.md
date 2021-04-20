<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.platform.core.juniper_junos.sync_platform

scrapli_cfg.platform.core.juniper_junos.sync_platform

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_cfg.platform.core.juniper_junos.sync_platform"""
from typing import Any, Callable, List, Optional

from scrapli.driver import NetworkDriver
from scrapli.response import MultiResponse, Response
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.exceptions import DiffConfigError
from scrapli_cfg.platform.base.sync_platform import ScrapliCfgPlatform
from scrapli_cfg.platform.core.juniper_junos.base_platform import (
    CONFIG_SOURCES,
    JUNOS_ADDTL_PRIVS,
    ScrapliCfgJunosBase,
)
from scrapli_cfg.response import ScrapliCfgResponse


def junos_on_open(cls: ScrapliCfgPlatform) -> None:
    """
    Scrapli CFG Junos On open

    Nothing for now I think...? Keeping this here for consistency.

    Args:
        cls: ScrapliCfg object

    Returns:
        None

    Raises:
        N/A

    """
    _ = cls


class ScrapliCfgJunos(ScrapliCfgPlatform, ScrapliCfgJunosBase):
    def __init__(
        self,
        conn: NetworkDriver,
        config_sources: Optional[List[str]] = None,
        on_open: Optional[Callable[..., Any]] = None,
        filesystem: str = "/config/",
        cleanup_post_commit: bool = True,
        preserve_connection: bool = False,
    ) -> None:
        if config_sources is None:
            config_sources = CONFIG_SOURCES

        if on_open is None:
            on_open = junos_on_open

        super().__init__(
            conn=conn,
            config_sources=config_sources,
            on_open=on_open,
            preserve_connection=preserve_connection,
        )

        self.filesystem = filesystem

        self._replace = False
        self._set = False

        self.candidate_config_filename = ""
        self._in_configuration_session = False

        self.cleanup_post_commit = cleanup_post_commit

        original_privs = self.conn.privilege_levels
        updated_privs = {**original_privs, **JUNOS_ADDTL_PRIVS}
        self.conn.privilege_levels = updated_privs
        self.conn.update_privilege_levels()

    def _delete_candidate_config(self) -> Response:
        """
        Delete candidate config from the filesystem

        Args:
            N/A

        Returns:
            Response: response from deleting the candidate config

        Raises:
            N/A

        """
        delete_result = self.conn.send_config(
            config=f"rm {self.filesystem}{self.candidate_config_filename}",
            privilege_level="root_shell",
        )
        return delete_result

    def get_version(self) -> ScrapliCfgResponse:
        response = self._pre_get_version()

        version_result = self.conn.send_command(command="show version | grep junos:")

        return self._post_get_version(
            response=response,
            scrapli_responses=[version_result],
            result=self._parse_version(device_output=version_result.result),
        )

    def get_config(self, source: str = "running") -> ScrapliCfgResponse:
        response = self._pre_get_config(source=source)

        if self._in_configuration_session is True:
            config_result = self.conn.send_config(config="run show configuration")
        else:
            config_result = self.conn.send_command(command="show configuration")

        return self._post_get_config(
            response=response,
            source=source,
            scrapli_responses=[config_result],
            result=config_result.result,
        )

    def load_config(self, config: str, replace: bool = False, **kwargs: Any) -> ScrapliCfgResponse:
        """
        Load configuration to a device

        Supported kwargs:
            set: bool indicating config is a "set" style config (ignored if replace is True)

        Args:
            config: string of the configuration to load
            replace: replace the configuration or not, if false configuration will be loaded as a
                merge operation
            kwargs: additional kwargs that the implementing classes may need for their platform,
                see above for junos supported kwargs

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """
        self._set = kwargs.get("set", False)

        response = self._pre_load_config(config=config)

        config = self._prepare_load_config(config=config, replace=replace)

        config_result = self.conn.send_config(config=config, privilege_level="root_shell")

        if self._replace is True:
            load_config = f"load override {self.filesystem}{self.candidate_config_filename}"
        else:
            if self._set is True:
                load_config = f"load set {self.filesystem}{self.candidate_config_filename}"
            else:
                load_config = f"load merge {self.filesystem}{self.candidate_config_filename}"

        load_result = self.conn.send_config(config=load_config)
        self._in_configuration_session = True

        return self._post_load_config(
            response=response,
            scrapli_responses=[config_result, load_result],
        )

    def abort_config(self) -> ScrapliCfgResponse:
        response = self._pre_abort_config(
            session_or_config_file=bool(self.candidate_config_filename)
        )

        abort_result = self._delete_candidate_config()
        rollback_result = self.conn.send_config(config="rollback 0")
        self._reset_config_session()

        return self._post_abort_config(
            response=response, scrapli_responses=[abort_result, rollback_result]
        )

    def commit_config(self, source: str = "running") -> ScrapliCfgResponse:
        scrapli_responses = []
        response = self._pre_commit_config(
            source=source, session_or_config_file=bool(self.candidate_config_filename)
        )

        commit_result = self.conn.send_config(config="commit")
        scrapli_responses.append(commit_result)

        if self.cleanup_post_commit:
            cleanup_result = self._delete_candidate_config()
            scrapli_responses.append(cleanup_result)

        self._reset_config_session()

        return self._post_load_config(
            response=response,
            scrapli_responses=scrapli_responses,
        )

    def diff_config(self, source: str = "running") -> ScrapliCfgDiffResponse:
        scrapli_responses = []
        device_diff = ""
        source_config = ""

        diff_response = self._pre_diff_config(
            source=source, session_or_config_file=bool(self.candidate_config_filename)
        )

        try:
            diff_result = self.conn.send_config(config="show | compare")
            scrapli_responses.append(diff_result)
            if diff_result.failed:
                msg = "failed generating diff for config session"
                self.logger.critical(msg)
                raise DiffConfigError(msg)

            device_diff = diff_result.result

            source_config_result = self.get_config(source=source)
            source_config = source_config_result.result

            if isinstance(source_config_result.scrapli_responses, MultiResponse):
                # in this case this will always be a multiresponse or nothing (failure) but mypy
                # doesnt know that, hence the isinstance check
                scrapli_responses.extend(source_config_result.scrapli_responses)

            if source_config_result.failed:
                msg = "failed fetching source config for diff comparison"
                self.logger.critical(msg)
                raise DiffConfigError(msg)

        except DiffConfigError:
            pass

        source_config, candidate_config = self._normalize_source_candidate_configs(
            source_config=source_config
        )

        return self._post_diff_config(
            diff_response=diff_response,
            scrapli_responses=scrapli_responses,
            source_config=source_config,
            candidate_config=candidate_config,
            device_diff=device_diff,
        )
        </code>
    </pre>
</details>



## Functions

    

#### junos_on_open
`junos_on_open(cls: scrapli_cfg.platform.base.sync_platform.ScrapliCfgPlatform) ‑> NoneType`

```text
Scrapli CFG Junos On open

Nothing for now I think...? Keeping this here for consistency.

Args:
    cls: ScrapliCfg object

Returns:
    None

Raises:
    N/A
```




## Classes

### ScrapliCfgJunos


```text
Helper class that provides a standard way to create an ABC using
inheritance.

Scrapli Config base class

Args:
    conn: scrapli connection to use
    config_sources: list of config sources
    on_open: async callable to run at connection open
    preserve_connection: if True underlying scrapli connection will *not* be closed when
        the scrapli_cfg object is closed/exited

Returns:
    None

Raises:
    N/A
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class ScrapliCfgJunos(ScrapliCfgPlatform, ScrapliCfgJunosBase):
    def __init__(
        self,
        conn: NetworkDriver,
        config_sources: Optional[List[str]] = None,
        on_open: Optional[Callable[..., Any]] = None,
        filesystem: str = "/config/",
        cleanup_post_commit: bool = True,
        preserve_connection: bool = False,
    ) -> None:
        if config_sources is None:
            config_sources = CONFIG_SOURCES

        if on_open is None:
            on_open = junos_on_open

        super().__init__(
            conn=conn,
            config_sources=config_sources,
            on_open=on_open,
            preserve_connection=preserve_connection,
        )

        self.filesystem = filesystem

        self._replace = False
        self._set = False

        self.candidate_config_filename = ""
        self._in_configuration_session = False

        self.cleanup_post_commit = cleanup_post_commit

        original_privs = self.conn.privilege_levels
        updated_privs = {**original_privs, **JUNOS_ADDTL_PRIVS}
        self.conn.privilege_levels = updated_privs
        self.conn.update_privilege_levels()

    def _delete_candidate_config(self) -> Response:
        """
        Delete candidate config from the filesystem

        Args:
            N/A

        Returns:
            Response: response from deleting the candidate config

        Raises:
            N/A

        """
        delete_result = self.conn.send_config(
            config=f"rm {self.filesystem}{self.candidate_config_filename}",
            privilege_level="root_shell",
        )
        return delete_result

    def get_version(self) -> ScrapliCfgResponse:
        response = self._pre_get_version()

        version_result = self.conn.send_command(command="show version | grep junos:")

        return self._post_get_version(
            response=response,
            scrapli_responses=[version_result],
            result=self._parse_version(device_output=version_result.result),
        )

    def get_config(self, source: str = "running") -> ScrapliCfgResponse:
        response = self._pre_get_config(source=source)

        if self._in_configuration_session is True:
            config_result = self.conn.send_config(config="run show configuration")
        else:
            config_result = self.conn.send_command(command="show configuration")

        return self._post_get_config(
            response=response,
            source=source,
            scrapli_responses=[config_result],
            result=config_result.result,
        )

    def load_config(self, config: str, replace: bool = False, **kwargs: Any) -> ScrapliCfgResponse:
        """
        Load configuration to a device

        Supported kwargs:
            set: bool indicating config is a "set" style config (ignored if replace is True)

        Args:
            config: string of the configuration to load
            replace: replace the configuration or not, if false configuration will be loaded as a
                merge operation
            kwargs: additional kwargs that the implementing classes may need for their platform,
                see above for junos supported kwargs

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """
        self._set = kwargs.get("set", False)

        response = self._pre_load_config(config=config)

        config = self._prepare_load_config(config=config, replace=replace)

        config_result = self.conn.send_config(config=config, privilege_level="root_shell")

        if self._replace is True:
            load_config = f"load override {self.filesystem}{self.candidate_config_filename}"
        else:
            if self._set is True:
                load_config = f"load set {self.filesystem}{self.candidate_config_filename}"
            else:
                load_config = f"load merge {self.filesystem}{self.candidate_config_filename}"

        load_result = self.conn.send_config(config=load_config)
        self._in_configuration_session = True

        return self._post_load_config(
            response=response,
            scrapli_responses=[config_result, load_result],
        )

    def abort_config(self) -> ScrapliCfgResponse:
        response = self._pre_abort_config(
            session_or_config_file=bool(self.candidate_config_filename)
        )

        abort_result = self._delete_candidate_config()
        rollback_result = self.conn.send_config(config="rollback 0")
        self._reset_config_session()

        return self._post_abort_config(
            response=response, scrapli_responses=[abort_result, rollback_result]
        )

    def commit_config(self, source: str = "running") -> ScrapliCfgResponse:
        scrapli_responses = []
        response = self._pre_commit_config(
            source=source, session_or_config_file=bool(self.candidate_config_filename)
        )

        commit_result = self.conn.send_config(config="commit")
        scrapli_responses.append(commit_result)

        if self.cleanup_post_commit:
            cleanup_result = self._delete_candidate_config()
            scrapli_responses.append(cleanup_result)

        self._reset_config_session()

        return self._post_load_config(
            response=response,
            scrapli_responses=scrapli_responses,
        )

    def diff_config(self, source: str = "running") -> ScrapliCfgDiffResponse:
        scrapli_responses = []
        device_diff = ""
        source_config = ""

        diff_response = self._pre_diff_config(
            source=source, session_or_config_file=bool(self.candidate_config_filename)
        )

        try:
            diff_result = self.conn.send_config(config="show | compare")
            scrapli_responses.append(diff_result)
            if diff_result.failed:
                msg = "failed generating diff for config session"
                self.logger.critical(msg)
                raise DiffConfigError(msg)

            device_diff = diff_result.result

            source_config_result = self.get_config(source=source)
            source_config = source_config_result.result

            if isinstance(source_config_result.scrapli_responses, MultiResponse):
                # in this case this will always be a multiresponse or nothing (failure) but mypy
                # doesnt know that, hence the isinstance check
                scrapli_responses.extend(source_config_result.scrapli_responses)

            if source_config_result.failed:
                msg = "failed fetching source config for diff comparison"
                self.logger.critical(msg)
                raise DiffConfigError(msg)

        except DiffConfigError:
            pass

        source_config, candidate_config = self._normalize_source_candidate_configs(
            source_config=source_config
        )

        return self._post_diff_config(
            diff_response=diff_response,
            scrapli_responses=scrapli_responses,
            source_config=source_config,
            candidate_config=candidate_config,
            device_diff=device_diff,
        )
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.platform.base.sync_platform.ScrapliCfgPlatform
- abc.ABC
- scrapli_cfg.platform.base.base_platform.ScrapliCfgBase
- scrapli_cfg.platform.core.juniper_junos.base_platform.ScrapliCfgJunosBase
#### Class variables

    
`conn: Union[scrapli.driver.network.sync_driver.NetworkDriver, scrapli.driver.network.async_driver.AsyncNetworkDriver]`



#### Methods

    

##### load_config
`load_config(self, config: str, replace: bool = False, **kwargs: Any) ‑> scrapli_cfg.response.ScrapliCfgResponse`

```text
Load configuration to a device

Supported kwargs:
    set: bool indicating config is a "set" style config (ignored if replace is True)

Args:
    config: string of the configuration to load
    replace: replace the configuration or not, if false configuration will be loaded as a
        merge operation
    kwargs: additional kwargs that the implementing classes may need for their platform,
        see above for junos supported kwargs

Returns:
    ScrapliCfgResponse: response object

Raises:
    N/A
```