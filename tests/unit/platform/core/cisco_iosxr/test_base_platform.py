import pytest

IOSXE_SHOW_VERSION_OUTPUT = """Sat Mar  6 21:35:16.805 UTC
Cisco IOS XR Software, Version 6.5.3
Copyright (c) 2013-2019 by Cisco Systems, Inc.

Build Information:
 Built By     : ahoang
 Built On     : Tue Mar 26 06:52:25 PDT 2019
 Built Host   : iox-ucs-019
 Workspace    : /auto/srcarchive13/prod/6.5.3/xrv9k/ws
 Version      : 6.5.3
 Location     : /opt/cisco/XR/packages/

cisco IOS-XRv 9000 () processor
System uptime is 5 hours 46 minutes"""

CONFIG_PAYLOAD = """Sat Mar  6 21:36:58.107 UTC
Building configuration...
!! IOS XR Configuration version = 6.5.3
!! Last configuration change at Thu Mar  4 01:30:30 2021 by vrnetlab
!
telnet vrf default ipv4 server max-servers 10
banner motd ^
something in a banner
^
end"""


def test_parse_version_success(iosxr_base_cfg_object):
    actual_version_string = iosxr_base_cfg_object._parse_version(
        device_output=IOSXE_SHOW_VERSION_OUTPUT
    )
    assert actual_version_string == "6.5.3"


def test_parse_version_no_match(iosxr_base_cfg_object):
    actual_version_string = iosxr_base_cfg_object._parse_version(device_output="blah")
    assert actual_version_string == ""


def test_prepare_config_payloads(iosxr_base_cfg_object):
    actual_config, actual_eager_config = iosxr_base_cfg_object._prepare_config_payloads(
        config=CONFIG_PAYLOAD
    )
    assert actual_config == "!\n!\n!\n!\n!\ntelnet vrf default ipv4 server max-servers 10\n!\n!"
    assert actual_eager_config == "banner motd ^\nsomething in a banner\n^"


def test_prepare_load_config_session_and_payload(iosxr_base_cfg_object):
    (
        actual_config,
        actual_eager_config,
    ) = iosxr_base_cfg_object._prepare_load_config_session_and_payload(
        config=CONFIG_PAYLOAD,
        replace=True,
        exclusive=False,
    )
    assert iosxr_base_cfg_object._in_configuration_session is True
    assert iosxr_base_cfg_object._config_privilege_level == "configuration"
    assert iosxr_base_cfg_object.candidate_config == CONFIG_PAYLOAD
    assert actual_config == "!\n!\n!\n!\n!\ntelnet vrf default ipv4 server max-servers 10\n!\n!"
    assert actual_eager_config == "banner motd ^\nsomething in a banner\n^"


def test_reset_config_session(iosxr_base_cfg_object, dummy_logger):
    iosxr_base_cfg_object.logger = dummy_logger
    iosxr_base_cfg_object._in_configuration_session = True
    iosxr_base_cfg_object._config_privilege_level = "BLAH"
    iosxr_base_cfg_object.candidate_config = "SOMECONFIG"

    iosxr_base_cfg_object._reset_config_session()

    iosxr_base_cfg_object._in_configuration_session = False
    iosxr_base_cfg_object._config_privilege_level = ""
    iosxr_base_cfg_object.candidate_config = ""


@pytest.mark.parametrize(
    "test_data",
    (
        (
            True,
            "show configuration changes diff",
        ),
        (
            False,
            "show commit changes diff",
        ),
    ),
    ids=(
        "replace",
        "merge",
    ),
)
def test_get_diff_command(iosxr_base_cfg_object, test_data):
    replace, expected_command = test_data
    iosxr_base_cfg_object._replace = replace
    assert iosxr_base_cfg_object._get_diff_command() == expected_command


def test_normalize_source_candidate_configs(iosxr_base_cfg_object, dummy_logger):
    iosxr_base_cfg_object.logger = dummy_logger

    iosxr_base_cfg_object.candidate_config = CONFIG_PAYLOAD
    (
        actual_source_config,
        actual_candidate_config,
    ) = iosxr_base_cfg_object._normalize_source_candidate_configs(source_config=CONFIG_PAYLOAD)

    assert (
        actual_source_config
        == "!\ntelnet vrf default ipv4 server max-servers 10\nbanner motd ^\nsomething in a banner\n^\nend"
    )
    assert (
        actual_candidate_config
        == "!\ntelnet vrf default ipv4 server max-servers 10\nbanner motd ^\nsomething in a banner\n^\nend"
    )
