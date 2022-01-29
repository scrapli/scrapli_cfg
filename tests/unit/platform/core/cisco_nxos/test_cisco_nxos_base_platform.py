import pytest

from scrapli_cfg.exceptions import FailedToFetchSpaceAvailable, InsufficientSpaceAvailable
from scrapli_cfg.response import ScrapliCfgResponse

CONFIG_PAYLOAD = """!Command: show running-config
!Running configuration last done at: Sat Mar  6 15:58:28 2021
!Time: Sat Mar  6 22:27:03 2021
!#feature ssh
!#ssh key rsa 1024
version 9.2(4) Bios:version"""

FLASH_BYTES_OUTPUT = " 1950670848 bytes free"
NXOS_SHOW_VERSION_OUTPUT = """Cisco Nexus Operating System (NX-OS) Software
TAC support: http://www.cisco.com/tac
Documents: http://www.cisco.com/en/US/products/ps9372/tsd_products_support_series_home.html
Copyright (c) 2002-2019, Cisco Systems, Inc. All rights reserved.
The copyrights to certain works contained herein are owned by
other third parties and are used and distributed under license.
Some parts of this software are covered under the GNU Public
License. A copy of the license is available at
http://www.gnu.org/licenses/gpl.html.

Nexus 9000v is a demo version of the Nexus Operating System

Software
  BIOS: version
 NXOS: version 9.2(4)
  BIOS compile time:
  NXOS image file is: bootflash:///nxos.9.2.4.bin
  NXOS compile time:  8/20/2019 7:00:00 [08/20/2019 15:52:22]


Hardware
  cisco Nexus9000 9000v Chassis
   with 8159680 kB of memory.
  Processor Board ID 9HV124BGIKU

  Device name: switch
  bootflash:    3509454 kB
Kernel uptime is 0 day(s), 6 hour(s), 28 minute(s), 42 second(s)

Last reset
  Reason: Unknown
  System version:
  Service:

plugin
  Core Plugin, Ethernet Plugin

Active Package(s):"""


def test_post_get_filesystem_space_available(nxos_base_cfg_object, dummy_logger):
    nxos_base_cfg_object.logger = dummy_logger

    actual_bytes_available = nxos_base_cfg_object._post_get_filesystem_space_available(
        output=FLASH_BYTES_OUTPUT
    )
    assert actual_bytes_available == 1950670848

    with pytest.raises(FailedToFetchSpaceAvailable):
        nxos_base_cfg_object._post_get_filesystem_space_available(output="NOTHING")


def test_space_available(nxos_base_cfg_object, dummy_logger):
    nxos_base_cfg_object.logger = dummy_logger

    nxos_base_cfg_object._filesystem_space_available_buffer_perc = 100
    nxos_base_cfg_object.candidate_config = "a"
    nxos_base_cfg_object._space_available(filesystem_bytes_available=3)

    # candidate config size is judged off of length -- in this case we have two char w/ 100% buffer
    # perc, so we will actually need 4bytes, but we'll pretend there are only 3 available
    nxos_base_cfg_object.candidate_config = "ab"
    with pytest.raises(InsufficientSpaceAvailable):
        nxos_base_cfg_object._space_available(filesystem_bytes_available=3)


def test_parse_version_success(nxos_base_cfg_object):
    actual_version_string = nxos_base_cfg_object._parse_version(
        device_output=NXOS_SHOW_VERSION_OUTPUT
    )
    assert actual_version_string == "9.2(4)"


def test_parse_version_no_match(nxos_base_cfg_object):
    actual_version_string = nxos_base_cfg_object._parse_version(device_output="blah")
    assert actual_version_string == ""


def test_reset_config_session(nxos_base_cfg_object, dummy_logger):
    nxos_base_cfg_object.logger = dummy_logger
    nxos_base_cfg_object.candidate_config_filename = "BLAH"
    nxos_base_cfg_object.candidate_config = "SOMECONFIG"

    nxos_base_cfg_object._reset_config_session()

    assert nxos_base_cfg_object.candidate_config_filename == ""
    assert nxos_base_cfg_object.candidate_config == ""


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
def test_get_config_command(nxos_base_cfg_object, test_data):
    source, expected_command = test_data
    assert nxos_base_cfg_object._get_config_command(source=source) == expected_command


@pytest.mark.parametrize(
    "test_data",
    (
        (
            True,
            "show diff rollback-patch running-config file bootflash:scrapli_cfg_candidate",
        ),
        (
            False,
            "",
        ),
    ),
    ids=(
        "replace",
        "merge",
    ),
)
def test_get_diff_command(nxos_base_cfg_object, test_data):
    replace, expected_command = test_data
    nxos_base_cfg_object._replace = replace
    nxos_base_cfg_object.filesystem = "bootflash:"
    nxos_base_cfg_object.candidate_config_filename = "scrapli_cfg_candidate"
    assert nxos_base_cfg_object._get_diff_command(source="running") == expected_command


def test_prepare_config_payloads(nxos_base_cfg_object):
    nxos_base_cfg_object.filesystem = "bootflash:"
    nxos_base_cfg_object.candidate_config_filename = "scrapli_cfg_candidate"
    actual_config = nxos_base_cfg_object._prepare_config_payloads(
        config="interface loopback123\n  description tacocat"
    )
    assert (
        actual_config
        == """set fl [open "/bootflash/scrapli_cfg_candidate" wb+]\nputs -nonewline $fl {interface loopback123\r}\nputs -nonewline $fl {  description tacocat\r}\nclose $fl"""
    )


def test_prepare_load_config(nxos_base_cfg_object, dummy_logger):
    nxos_base_cfg_object.logger = dummy_logger
    nxos_base_cfg_object.candidate_config_filename = ""
    nxos_base_cfg_object.filesystem = "bootflash:"
    actual_config = nxos_base_cfg_object._prepare_load_config(
        config="interface loopback123\n  description tacocat", replace=True
    )
    assert nxos_base_cfg_object.candidate_config == "interface loopback123\n  description tacocat"
    assert nxos_base_cfg_object._replace is True
    # dont wanna deal w/ finding the timestamp stuff, so we'll just make sure the rest of the actual
    # config is what we think it shoudl be
    assert actual_config.startswith("""set fl [open "/bootflash/scrapli_cfg_""")
    assert actual_config.endswith(
        """wb+]\nputs -nonewline $fl {interface loopback123\r}\nputs -nonewline $fl {  description tacocat\r}\nclose $fl"""
    )


def test_clean_config(nxos_base_cfg_object, dummy_logger):
    nxos_base_cfg_object.logger = dummy_logger
    nxos_base_cfg_object.candidate_config = CONFIG_PAYLOAD

    actual_config = nxos_base_cfg_object.clean_config(config=CONFIG_PAYLOAD)
    assert actual_config == "version 9.2(4) Bios:version"


def test_pre_get_checkpoint(nxos_base_cfg_object, dummy_logger, sync_scrapli_conn):
    nxos_base_cfg_object.logger = dummy_logger
    nxos_base_cfg_object.conn = sync_scrapli_conn
    nxos_base_cfg_object.filesystem = "bootflash:"

    response, actual_commands = nxos_base_cfg_object._pre_get_checkpoint(
        conn=nxos_base_cfg_object.conn
    )

    assert isinstance(response, ScrapliCfgResponse)
    assert actual_commands[0] == "terminal dont-ask"
    assert actual_commands[1].startswith("checkpoint file bootflash:scrapli_cfg_tmp_")
    assert actual_commands[2].startswith("show file bootflash:scrapli_cfg_tmp_")
    assert actual_commands[3].startswith("delete bootflash:scrapli_cfg_tmp_")
