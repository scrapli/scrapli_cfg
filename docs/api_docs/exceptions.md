<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_cfg.exceptions

scrapli_cfg.exceptions

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_cfg.exceptions"""
from scrapli.exceptions import ScrapliException


class ScrapliCfgException(ScrapliException):
    """Base scrapli_cfg exception"""


class TemplateError(ScrapliCfgException):
    """For errors relating to configuration templates"""


class FailedToDetermineDeviceState(ScrapliCfgException):
    """For issues determining device state (i.e. what mode is file prompt in, etc.)"""


class VersionError(ScrapliCfgException):
    """For errors related to getting/parsing/invalid versions"""


class ConfigError(ScrapliCfgException):
    """For configuration operation related errors"""


class InvalidConfigTarget(ConfigError):
    """User has provided an invalid configuration target"""


class FailedToFetchSpaceAvailable(ConfigError):
    """Unable to determine space available on filesystem"""


class InsufficientSpaceAvailable(ConfigError):
    """If space available on filesystem is insufficient"""


class GetConfigError(ConfigError):
    """For errors getting configuration from a device"""


class LoadConfigError(ConfigError):
    """For errors loading a configuration"""


class DiffConfigError(ConfigError):
    """For errors diffing a configuration"""


class AbortConfigError(ConfigError):
    """For errors aborting a configuration"""


class CommitConfigError(ConfigError):
    """For errors committing a configuration"""


class CleanupError(ScrapliCfgException):
    """For errors during cleanup (i.e. removing candidate config, etc.)"""
        </code>
    </pre>
</details>




## Classes

### AbortConfigError


```text
For errors aborting a configuration
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class AbortConfigError(ConfigError):
    """For errors aborting a configuration"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ConfigError
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException



### CleanupError


```text
For errors during cleanup (i.e. removing candidate config, etc.)
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class CleanupError(ScrapliCfgException):
    """For errors during cleanup (i.e. removing candidate config, etc.)"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException



### CommitConfigError


```text
For errors committing a configuration
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class CommitConfigError(ConfigError):
    """For errors committing a configuration"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ConfigError
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException



### ConfigError


```text
For configuration operation related errors
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class ConfigError(ScrapliCfgException):
    """For configuration operation related errors"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException
#### Descendants
- scrapli_cfg.exceptions.AbortConfigError
- scrapli_cfg.exceptions.CommitConfigError
- scrapli_cfg.exceptions.DiffConfigError
- scrapli_cfg.exceptions.FailedToFetchSpaceAvailable
- scrapli_cfg.exceptions.GetConfigError
- scrapli_cfg.exceptions.InsufficientSpaceAvailable
- scrapli_cfg.exceptions.InvalidConfigTarget
- scrapli_cfg.exceptions.LoadConfigError



### DiffConfigError


```text
For errors diffing a configuration
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class DiffConfigError(ConfigError):
    """For errors diffing a configuration"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ConfigError
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException



### FailedToDetermineDeviceState


```text
For issues determining device state (i.e. what mode is file prompt in, etc.)
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class FailedToDetermineDeviceState(ScrapliCfgException):
    """For issues determining device state (i.e. what mode is file prompt in, etc.)"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException



### FailedToFetchSpaceAvailable


```text
Unable to determine space available on filesystem
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class FailedToFetchSpaceAvailable(ConfigError):
    """Unable to determine space available on filesystem"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ConfigError
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException



### GetConfigError


```text
For errors getting configuration from a device
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class GetConfigError(ConfigError):
    """For errors getting configuration from a device"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ConfigError
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException



### InsufficientSpaceAvailable


```text
If space available on filesystem is insufficient
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class InsufficientSpaceAvailable(ConfigError):
    """If space available on filesystem is insufficient"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ConfigError
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException



### InvalidConfigTarget


```text
User has provided an invalid configuration target
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class InvalidConfigTarget(ConfigError):
    """User has provided an invalid configuration target"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ConfigError
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException



### LoadConfigError


```text
For errors loading a configuration
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class LoadConfigError(ConfigError):
    """For errors loading a configuration"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ConfigError
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException



### ScrapliCfgException


```text
Base scrapli_cfg exception
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class ScrapliCfgException(ScrapliException):
    """Base scrapli_cfg exception"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException
#### Descendants
- scrapli_cfg.exceptions.CleanupError
- scrapli_cfg.exceptions.ConfigError
- scrapli_cfg.exceptions.FailedToDetermineDeviceState
- scrapli_cfg.exceptions.TemplateError
- scrapli_cfg.exceptions.VersionError



### TemplateError


```text
For errors relating to configuration templates
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class TemplateError(ScrapliCfgException):
    """For errors relating to configuration templates"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException



### VersionError


```text
For errors related to getting/parsing/invalid versions
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class VersionError(ScrapliCfgException):
    """For errors related to getting/parsing/invalid versions"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_cfg.exceptions.ScrapliCfgException
- scrapli.exceptions.ScrapliException
- builtins.Exception
- builtins.BaseException