"""scrapli_cfg.exceptions"""
from typing import Optional

from scrapli.exceptions import ScrapliException


class ScrapliCfgException(ScrapliException):
    """Base scrapli_cfg exception"""


class PrepareNotCalled(ScrapliCfgException):
    """Raised when the `prepare` method has not been called and strict_prepare is `True`"""

    def __init__(
        self,
        message: Optional[str] = None,
    ) -> None:
        """
        Scrapli Cfg prepare not called exception

        Args:
            message: optional message

        Returns:
            None

        Raises:
            N/A

        """
        if not message:
            self.message = (
                "strict_prepare is True and you are attempting to call a method that requires "
                "prepare to have been called, do you need to call 'prepare()'?"
            )
        else:
            self.message = message
        super().__init__(self.message)


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
