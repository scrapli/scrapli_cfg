import pytest

from scrapli_cfg.exceptions import FailedToFetchSpaceAvailable, InsufficientSpaceAvailable
from scrapli_cfg.response import ScrapliCfgResponse

CONFIG_PAYLOAD = """## Last commit: 2021-03-07 18:30:28 UTC by vrnetlab
version 17.3R2.10;
system {
"""

FLASH_BYTES_OUTPUT = " 1950670848 bytes free"
JUNOS_SHOW_VERSION_OUTPUT = """Junos: 17.3R2.10
"""


def test_parse_version_success(junos_base_cfg_object):
    actual_version_string = junos_base_cfg_object._parse_version(
        device_output=JUNOS_SHOW_VERSION_OUTPUT
    )
    assert actual_version_string == "17.3R2.10"


def test_parse_version_no_match(junos_base_cfg_object):
    actual_version_string = junos_base_cfg_object._parse_version(device_output="blah")
    assert actual_version_string == ""


def test_reset_config_session(junos_base_cfg_object, dummy_logger):
    junos_base_cfg_object.logger = dummy_logger
    junos_base_cfg_object.candidate_config_filename = "BLAH"
    junos_base_cfg_object.candidate_config = "SOMECONFIG"
    junos_base_cfg_object._in_configuration_session = True
    junos_base_cfg_object._set = True

    junos_base_cfg_object._reset_config_session()

    assert junos_base_cfg_object.candidate_config_filename == ""
    assert junos_base_cfg_object.candidate_config == ""
    assert junos_base_cfg_object._in_configuration_session is False
    assert junos_base_cfg_object._set is False


def test_prepare_config_payloads(junos_base_cfg_object):
    junos_base_cfg_object.filesystem = "/config/"
    junos_base_cfg_object.candidate_config_filename = "scrapli_cfg_candidate"
    actual_config = junos_base_cfg_object._prepare_config_payloads(
        config="interface fxp0\n  description tacocat"
    )
    assert (
        actual_config
        == """echo >> /config/scrapli_cfg_candidate 'interface fxp0'\necho >> /config/scrapli_cfg_candidate '  description tacocat'"""
    )


def test_prepare_load_config(junos_base_cfg_object, dummy_logger):
    junos_base_cfg_object.logger = dummy_logger
    junos_base_cfg_object.candidate_config_filename = ""
    junos_base_cfg_object.filesystem = "/config/"
    actual_config = junos_base_cfg_object._prepare_load_config(
        config="interface fxp0\n  description tacocat", replace=True
    )
    assert junos_base_cfg_object.candidate_config == "interface fxp0\n  description tacocat"
    assert junos_base_cfg_object._replace is True
    # dont wanna deal w/ finding the timestamp stuff, so we'll just make sure the rest of the actual
    # config is what we think it shoudl be
    assert actual_config.startswith("""echo >> /config/scrapli_cfg_""")
    assert actual_config.endswith("""description tacocat'""")


def test_clean_config(junos_base_cfg_object, dummy_logger):
    junos_base_cfg_object.logger = dummy_logger
    junos_base_cfg_object.candidate_config = CONFIG_PAYLOAD

    actual_config = junos_base_cfg_object.clean_config(config=CONFIG_PAYLOAD)

    assert actual_config == "system {"
