"""scrapli_cfg.exceptions"""

from scrapli.exceptions import ScrapliException


class ScrapliCfgException(ScrapliException):
    """Base scrapli_cfg exception"""


class PrepareNotCalled(ScrapliCfgException):
    """
    Raised when the `prepare` method has not been called

    This will only be raised in two scenarios:
    1) an `on_prepare` callable has been provided, yet `prepare` was not called
    2) `ignore_version` is False and `prepare` was not called

    If using a context manager this should never be raised as the enter method will handle things
    for you
    """


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
