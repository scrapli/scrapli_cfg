import pytest

from scrapli import Scrapli
from scrapli.response import Response
from scrapli_cfg.response import ScrapliCfgResponse

EOS_SHOW_VERSION_OUTPUT = """ vEOS
Hardware version:
Serial number:
System MAC address:  5254.001f.e379

Software image version: 4.22.1F
Architecture:           i686
Internal build version: 4.22.1F-13062802.4221F
Internal build ID:      bb097f5d-d38c-4c32-898b-c20f6e18b00a

Uptime:                 0 weeks, 0 days, 4 hours and 52 minutes
Total memory:           4008840 kB
Free memory:            3257488 kB"""

EOS_CONFIG_SESSION_OUTPUT = """{
    "maxSavedSessions": 1,
    "maxOpenSessions": 5,
    "sessions": {
        "racecar": {
            "description": "",
            "state": "pending",
            "instances": {}
        },
        "tacocat": {
            "description": "",
            "state": "pending",
            "instances": {}
        }
    }
}
"""

CONFIG_PAYLOAD = """! Command: show running-config
! device: localhost (vEOS, EOS-4.22.1F)
!
! boot system flash:/vEOS-lab.swi
!
switchport default mode routed
!
transceiver qsfp default-mode 4x10G
!
banner login
No startup-config was found.
EOF
!
end"""


def test_parse_version_success(eos_base_cfg_object):
    actual_version_string = eos_base_cfg_object._parse_version(
        device_output=EOS_SHOW_VERSION_OUTPUT
    )
    assert actual_version_string == "4.22.1F"


def test_parse_version_no_match(eos_base_cfg_object):
    actual_version_string = eos_base_cfg_object._parse_version(device_output="blah")
    assert actual_version_string == ""


def test_config_sessions(eos_base_cfg_object):
    actual_config_session_list = eos_base_cfg_object._parse_config_sessions(
        device_output=EOS_CONFIG_SESSION_OUTPUT
    )
    assert actual_config_session_list == ["racecar", "tacocat"]


def test_config_sessions_no_match(eos_base_cfg_object):
    actual_config_session_list = eos_base_cfg_object._parse_config_sessions(device_output="blah")
    assert actual_config_session_list == []


@pytest.mark.parametrize(
    "test_data",
    (
        ("running", "show running-config"),
        (
            "startup",
            "show startup-config",
        ),
    ),
    ids=(
        "running",
        "startup",
    ),
)
def test_get_config_command(eos_base_cfg_object, test_data):
    source, expected_command = test_data
    assert eos_base_cfg_object._get_config_command(source=source) == expected_command


def test_prepare_config_payloads(eos_base_cfg_object):
    actual_regular_config, actual_eager_config = eos_base_cfg_object._prepare_config_payloads(
        config=CONFIG_PAYLOAD
    )
    assert (
        actual_regular_config
        == "!\n!\n!\n!\n!\nswitchport default mode routed\n!\ntransceiver qsfp default-mode 4x10G\n!\n!\n!\n!"
    )
    assert actual_eager_config == "banner login\nNo startup-config was found.\nEOF"


def test_prepare_load_config_session_and_payloads(eos_base_cfg_object, dummy_logger):
    eos_base_cfg_object.logger = dummy_logger
    eos_base_cfg_object.config_session_name = ""
    (
        actual_regular_config,
        actual_eager_config,
        actual_register_config_session,
    ) = eos_base_cfg_object._prepare_load_config_session_and_payload(config=CONFIG_PAYLOAD)
    assert (
        actual_regular_config
        == "!\n!\n!\n!\n!\nswitchport default mode routed\n!\ntransceiver qsfp default-mode 4x10G\n!\n!\n!\n!"
    )
    assert actual_eager_config == "banner login\nNo startup-config was found.\nEOF"
    assert actual_register_config_session is True


def test_reset_config_session(eos_base_cfg_object, dummy_logger):
    eos_base_cfg_object.logger = dummy_logger
    eos_base_cfg_object.config_session_name = "BLAH"
    eos_base_cfg_object.candidate_config = "SOMECONFIG"

    eos_base_cfg_object._reset_config_session()

    assert eos_base_cfg_object.config_session_name == ""
    assert eos_base_cfg_object.candidate_config == ""


def test_clean_config(eos_base_cfg_object, dummy_logger):
    eos_base_cfg_object.logger = dummy_logger
    eos_base_cfg_object.candidate_config = CONFIG_PAYLOAD

    actual_config = eos_base_cfg_object.clean_config(config=CONFIG_PAYLOAD)

    # checking that this removes the comment banner basically, in the future it may have to "clean"
    # more things too
    assert (
        actual_config
        == "!\n!\nswitchport default mode routed\n!\ntransceiver qsfp default-mode 4x10G\n!\nbanner login\nNo startup-config was found.\nEOF\n!\nend"
    )


def test_pre_and_post_clear_config_sessions(eos_base_cfg_object, dummy_logger):
    eos_base_cfg_object.logger = dummy_logger
    eos_base_cfg_object.conn = Scrapli(host="localhost", platform="arista_eos")
    pre_response = eos_base_cfg_object._pre_clear_config_sessions()
    assert isinstance(pre_response, ScrapliCfgResponse)

    scrapli_response = Response(host="localhost", channel_input="diff a config")
    post_response = eos_base_cfg_object._post_clear_config_sessions(
        response=pre_response, scrapli_responses=[scrapli_response]
    )
    assert post_response.result == "failed to clear device configuration session(s)"

    scrapli_response.failed = False
    post_response = eos_base_cfg_object._post_clear_config_sessions(
        response=pre_response, scrapli_responses=[scrapli_response]
    )
    assert post_response.result == "configuration session(s) cleared"
