import pytest

from scrapli_cfg.exceptions import FailedToFetchSpaceAvailable, InsufficientSpaceAvailable
from scrapli_cfg.platform.core.cisco_iosxe.base_platform import FilePromptMode

CONFIG_PAYLOAD = """Building configuration...

Current configuration : 7020 bytes
!
! Last configuration change at 16:11:49 UTC Sat Mar 6 2021 by vrnetlab
!
version 16.12"""

FLASH_BYTES_OUTPUT = "6286540800 bytes total (5485645824 bytes free)"
IOSXE_SHOW_VERSION_OUTPUT = """Cisco IOS XE Software, Version 16.12.03
Cisco IOS Software [Gibraltar], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.12.3, RELEASE SOFTWARE (fc5)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2020 by Cisco Systems, Inc.
Compiled Mon 09-Mar-20 21:50 by mcpre


Cisco IOS-XE software, Copyright (c) 2005-2020 by cisco Systems, Inc.
All rights reserved.  Certain components of Cisco IOS-XE software are
licensed under the GNU General Public License ("GPL") Version 2.0.  The
software code licensed under GPL Version 2.0 is free software that comes
with ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such
GPL code under the terms of GPL Version 2.0.  For more details, see the
documentation or "License Notice" file accompanying the IOS-XE software,
or the applicable URL provided on the flyer accompanying the IOS-XE
software.


ROM: IOS-XE ROMMON

csr1000v uptime is 5 hours, 51 minutes
Uptime for this control processor is 5 hours, 52 minutes
System returned to ROM by reload
System image file is "bootflash:packages.conf"
Last reload reason: reload



This product contains cryptographic features and is subject to United
States and local country laws governing import, export, transfer and
use. Delivery of Cisco cryptographic products does not imply
third-party authority to import, export, distribute or use encryption.
Importers, exporters, distributors and users are responsible for
compliance with U.S. and local country laws. By using this product you
agree to comply with applicable laws and regulations. If you are unable
to comply with U.S. and local laws, return this product immediately.

A summary of U.S. laws governing Cisco cryptographic products may be found at:
http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

If you require further assistance please contact us by sending email to
export@cisco.com.

License Level: ax
License Type: N/A(Smart License Enabled)
Next reload license Level: ax


Smart Licensing Status: UNREGISTERED/No Licenses in Use

cisco CSR1000V (VXE) processor (revision VXE) with 2080230K/3075K bytes of memory.
Processor board ID 9MVVU09YZFH
10 Gigabit Ethernet interfaces
32768K bytes of non-volatile configuration memory.
3978344K bytes of physical memory.
6188032K bytes of virtual hard disk at bootflash:.
0K bytes of WebUI ODM Files at webui:.

Configuration register is 0x2102"""


def test_post_get_filesystem_space_available(iosxe_base_cfg_object, dummy_logger):
    iosxe_base_cfg_object.logger = dummy_logger

    actual_bytes_available = iosxe_base_cfg_object._post_get_filesystem_space_available(
        output=FLASH_BYTES_OUTPUT
    )
    assert actual_bytes_available == 5485645824

    with pytest.raises(FailedToFetchSpaceAvailable):
        iosxe_base_cfg_object._post_get_filesystem_space_available(output="NOTHING")


def test_space_available(iosxe_base_cfg_object, dummy_logger):
    iosxe_base_cfg_object.logger = dummy_logger

    iosxe_base_cfg_object._filesystem_space_available_buffer_perc = 100
    iosxe_base_cfg_object.candidate_config = "a"
    iosxe_base_cfg_object._space_available(filesystem_bytes_available=3)

    # candidate config size is judged off of length -- in this case we have two char w/ 100% buffer
    # perc, so we will actually need 4bytes, but we'll pretend there are only 3 available
    iosxe_base_cfg_object.candidate_config = "ab"
    with pytest.raises(InsufficientSpaceAvailable):
        iosxe_base_cfg_object._space_available(filesystem_bytes_available=3)


def test_post_determine_file_prompt_mode(iosxe_base_cfg_object, dummy_logger):
    iosxe_base_cfg_object.logger = dummy_logger

    assert iosxe_base_cfg_object._post_determine_file_prompt_mode(output="") == FilePromptMode.ALERT
    assert (
        iosxe_base_cfg_object._post_determine_file_prompt_mode(output="file prompt noisy")
        == FilePromptMode.NOISY
    )
    assert (
        iosxe_base_cfg_object._post_determine_file_prompt_mode(output="file prompt quiet")
        == FilePromptMode.QUIET
    )


def test_parse_version_success(iosxe_base_cfg_object):
    actual_version_string = iosxe_base_cfg_object._parse_version(
        device_output=IOSXE_SHOW_VERSION_OUTPUT
    )
    assert actual_version_string == "16.12.03"


def test_parse_version_no_match(iosxe_base_cfg_object):
    actual_version_string = iosxe_base_cfg_object._parse_version(device_output="blah")
    assert actual_version_string == ""


def test_clean_config(iosxe_base_cfg_object):
    assert iosxe_base_cfg_object.clean_config(config=CONFIG_PAYLOAD) == "version 16.12"


def test_reset_config_session(iosxe_base_cfg_object, dummy_logger):
    iosxe_base_cfg_object.logger = dummy_logger
    iosxe_base_cfg_object.candidate_config_filename = "BLAH"
    iosxe_base_cfg_object.candidate_config = "SOMECONFIG"

    iosxe_base_cfg_object._reset_config_session()

    assert iosxe_base_cfg_object.candidate_config_filename == ""
    assert iosxe_base_cfg_object.candidate_config == ""


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
def test_get_config_command(iosxe_base_cfg_object, test_data):
    source, expected_command = test_data
    assert iosxe_base_cfg_object._get_config_command(source=source) == expected_command


@pytest.mark.parametrize(
    "test_data",
    (
        (
            True,
            "show archive config differences system:running-config flash:scrapli_cfg_candidate",
        ),
        (
            False,
            "show archive config incremental-diffs flash:scrapli_cfg_candidate ignorecase",
        ),
    ),
    ids=(
        "replace",
        "merge",
    ),
)
def test_get_diff_command(iosxe_base_cfg_object, test_data):
    replace, expected_command = test_data
    iosxe_base_cfg_object._replace = replace
    iosxe_base_cfg_object.filesystem = "flash:"
    iosxe_base_cfg_object.candidate_config_filename = "scrapli_cfg_candidate"
    assert iosxe_base_cfg_object._get_diff_command(source="running") == expected_command


def test_prepare_config_payloads(iosxe_base_cfg_object):
    iosxe_base_cfg_object.filesystem = "flash:"
    iosxe_base_cfg_object.candidate_config_filename = "scrapli_cfg_candidate"
    actual_config = iosxe_base_cfg_object._prepare_config_payloads(
        config="interface loopback123\n  description tacocat"
    )
    assert (
        actual_config
        == """puts [open "flash:scrapli_cfg_candidate" w+] {\ninterface loopback123\n  description tacocat\n}"""
    )


def test_prepare_load_config(iosxe_base_cfg_object, dummy_logger):
    iosxe_base_cfg_object.logger = dummy_logger
    iosxe_base_cfg_object.candidate_config_filename = ""
    iosxe_base_cfg_object.filesystem = "flash:"
    actual_config = iosxe_base_cfg_object._prepare_load_config(
        config="interface loopback123\n  description tacocat", replace=True
    )
    assert iosxe_base_cfg_object.candidate_config == "interface loopback123\n  description tacocat"
    assert iosxe_base_cfg_object._replace is True
    # dont wanna deal w/ finding the timestamp stuff, so we'll just make sure the rest of the actual
    # config is what we think it shoudl be
    assert actual_config.startswith("""puts [open "flash:scrapli_cfg_""")
    assert actual_config.endswith("""w+] {\ninterface loopback123\n  description tacocat\n}""")


def test_normalize_source_candidate_configs(iosxe_base_cfg_object, dummy_logger):
    iosxe_base_cfg_object.logger = dummy_logger
    iosxe_base_cfg_object.candidate_config = CONFIG_PAYLOAD

    (
        actual_source_config,
        actual_candidate_config,
    ) = iosxe_base_cfg_object._normalize_source_candidate_configs(source_config=CONFIG_PAYLOAD)

    assert actual_source_config == "version 16.12"
    assert actual_candidate_config == "version 16.12"
