"""scrapli_cfg.platform.core.juniper_junos.sync_platform"""
# from typing import Any
#
# from scrapli.driver import NetworkDriver
# from scrapli_cfg.diff import ScrapliCfgDiff
# from scrapli_cfg.exceptions import DiffConfigError
# from scrapli_cfg.platforms.juniper_junos.base_platform import ScrapliCfgJunosBase
# from scrapli_cfg.platforms.sync_platform import ScrapliCfg
#
#
# class ScrapliCfgJunos(ScrapliCfgJunosBase, ScrapliCfg):
#     def __init__(
#         self,
#         conn: NetworkDriver,
#     ) -> None:
#         super().__init__(
#             conn=conn,
#         )
#
#     def on_open(self) -> None:
#         pass
#
#     def get_config(self, source: str = "running") -> str:
#         """
#         Get device configuration
#
#         Args:
#             source: name of the config source, generally running|startup
#
#         Returns:
#             str: string of the target config source
#
#         Raises:
#             N/A
#
#         """
#         get_config_command = self._pre_get_config(source=source)
#         if not self._in_configuration_session:
#             config_result = self.conn.send_command(command=get_config_command)
#         else:
#             config_result = self.conn.send_config(config=get_config_command)
#         return self._post_get_config(source=source, config_result=config_result)
#
#     def load_config(self, config: str, replace: bool = False, **kwargs: Any) -> None:
#         """
#         Load configuration to a device
#
#         Supported kwargs:
#             N/A
#
#         Args:
#             config: string of the configuration to load
#             replace: replace the configuration or not, if false configuration will be loaded as a
#                 merge operation
#             kwargs: additional kwargs that the implementing classes may need for their platform
#
#         Returns:
#             None
#
#         Raises:
#             N/A
#
#         """
#         config = self._pre_load_config(config=config, replace=replace)
#         config_result = self.conn.send_config(config=config, eager=True)
#         _ = config_result
#         breakpoint()
#
#     def diff_config(self, source: str = "running") -> ScrapliCfgDiff:
#         """
#         Diff a loaded configuration against the source config store
#
#         Args:
#             source: name of the config source to diff against, generally running|startup
#
#         Returns:
#             ScrapliCfgDiff: scrapli cfg diff object
#
#         Raises:
#             N/A
#
#         """
#         diff_command = "show | compare"
#         diff_result = self.conn.send_config(config=diff_command)
#
#         if diff_result.failed:
#             raise DiffConfigError("failed generating diff for config session")
#
#         source_config_result = self.get_config(source=source)
#
#         return self._post_diff_config(
#             host=self.conn.host,
#             source=source,
#             source_config=source_config_result,
#             device_diff=diff_result.result,
#         )
#
#     def abort_config(self) -> None:
#         """
#         Abort a configuration -- discards any loaded config
#
#         Args:
#             N/A
#
#         Returns:
#             None
#
#         Raises:
#             N/A
#
#         """
#         self._pre_abort_config()
#         self.conn._abort_config()  # pylint: disable=W0212
#         self._post_abort_config()
#
#     def commit_config(self, source: str = "running") -> None:
#         """
#         Commit a loaded configuration
#
#         Args:
#             source: name of the config source to commit against, generally running|startup
#
#         Returns:
#             None
#
#         Raises:
#             N/A
#
#         """
