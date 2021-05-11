from pathlib import Path

import pytest
from devices import CONFIG_REPLACER, DEVICES

import scrapli_cfg

TEST_DATA_PATH = f"{Path(scrapli_cfg.__file__).parents[1]}/tests/test_data"


@pytest.fixture(scope="session")
def test_data_path():
    """Fixture to provide path to test data files"""
    return TEST_DATA_PATH


@pytest.fixture(scope="session")
def test_devices_dict():
    """Fixture to return test devices dict"""
    return DEVICES


@pytest.fixture(scope="session")
def expected_configs():
    """Fixture to provide expected configs"""
    return {
        "arista_eos": open(f"{TEST_DATA_PATH}/expected/arista_eos").read(),
        "cisco_iosxe": open(f"{TEST_DATA_PATH}/expected/cisco_iosxe").read(),
        "cisco_nxos": open(f"{TEST_DATA_PATH}/expected/cisco_nxos").read(),
        "cisco_iosxr": open(f"{TEST_DATA_PATH}/expected/cisco_iosxr").read(),
        "juniper_junos": open(f"{TEST_DATA_PATH}/expected/juniper_junos").read(),
    }


@pytest.fixture(scope="session")
def test_devices_dict():
    """Fixture to return test devices dict"""
    return DEVICES


@pytest.fixture(scope="session")
def config_replacer_dict():
    """Fixture to return dict of config replacer helper functions"""
    return CONFIG_REPLACER
