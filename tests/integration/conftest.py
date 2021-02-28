import os

import pytest

from scrapli.driver.core import (  # AsyncJunosDriver,; JunosDriver,
    AsyncEOSDriver,
    AsyncIOSXEDriver,
    AsyncIOSXRDriver,
    AsyncNXOSDriver,
    EOSDriver,
    IOSXEDriver,
    IOSXRDriver,
    NXOSDriver,
)
from scrapli_cfg import AsyncScrapliCfg, ScrapliCfg

from .. import helper
from ..conftest import EXPECTED_CONFIGS

VROUTER_MODE = bool(os.environ.get("SCRAPLI_VROUTER", False))
USERNAME = "vrnetlab"
PASSWORD = "VR-netlab9"
TIMEOUT_SOCKET = 60
TIMEOUT_TRANSPORT = 60
TIMEOUT_OPS = 60
TELNET_TRANSPORTS = (
    "telnet",
    "asynctelnet",
)
DEVICES = {
    "cisco_iosxe": {
        "driver": IOSXEDriver,
        "async_driver": AsyncIOSXEDriver,
        "auth_username": USERNAME,
        "auth_password": PASSWORD,
        "auth_secondary": PASSWORD,
        "auth_strict_key": False,
        "host": "localhost" if VROUTER_MODE else "172.18.0.11",
        "port": 21022 if VROUTER_MODE else 22,
    },
    "cisco_nxos": {
        "driver": NXOSDriver,
        "async_driver": AsyncNXOSDriver,
        "auth_username": USERNAME,
        "auth_password": PASSWORD,
        "auth_secondary": PASSWORD,
        "auth_strict_key": False,
        "host": "localhost" if VROUTER_MODE else "172.18.0.12",
        "port": 22022 if VROUTER_MODE else 22,
    },
    "cisco_iosxr": {
        "driver": IOSXRDriver,
        "async_driver": AsyncIOSXRDriver,
        "auth_username": USERNAME,
        "auth_password": PASSWORD,
        "auth_secondary": PASSWORD,
        "auth_strict_key": False,
        "host": "localhost" if VROUTER_MODE else "172.18.0.13",
        "port": 23022 if VROUTER_MODE else 22,
    },
    "arista_eos": {
        "driver": EOSDriver,
        "async_driver": AsyncEOSDriver,
        "auth_username": USERNAME,
        "auth_password": PASSWORD,
        "auth_secondary": PASSWORD,
        "auth_strict_key": False,
        "host": "localhost" if VROUTER_MODE else "172.18.0.14",
        "port": 24022 if VROUTER_MODE else 22,
        "comms_ansi": True,
    },
    # commenting out till junos support added
    # "juniper_junos": {
    #     "driver": JunosDriver,
    #     "async_driver": AsyncJunosDriver,
    #     "auth_username": USERNAME,
    #     "auth_password": PASSWORD,
    #     "auth_secondary": PASSWORD,
    #     "auth_strict_key": False,
    #     "host": "localhost" if VROUTER_MODE else "172.18.0.15",
    #     "port": 25022 if VROUTER_MODE else 22,
    # },
}


@pytest.fixture(
    scope="function",
    params=[
        "cisco_iosxe",
        "cisco_nxos",
        "cisco_iosxr",
        "arista_eos",
    ],  # "juniper_junos"],
)
def device_type(request):
    yield request.param


@pytest.fixture(scope="function", params=["system", "ssh2", "paramiko", "telnet"])
def transport(request):
    yield request.param


@pytest.fixture(scope="function", params=["asyncssh", "asynctelnet"])
def async_transport(request):
    yield request.param


@pytest.fixture(scope="function")
def conn(device_type, transport):
    device = DEVICES[device_type].copy()
    driver = device.pop("driver")
    device.pop("async_driver")

    port = device.pop("port")
    if transport in TELNET_TRANSPORTS:
        port = port + 1

    conn = driver(
        **device,
        port=port,
        transport=transport,
        timeout_socket=TIMEOUT_SOCKET,
        timeout_transport=TIMEOUT_TRANSPORT,
        timeout_ops=TIMEOUT_OPS,
    )
    return conn, device_type


@pytest.fixture(scope="function")
def cfg_conn(conn):
    scrapli_conn, device_type = conn
    cfg_conn = ScrapliCfg(conn=scrapli_conn, platform=device_type)

    cfg_conn._expected_config = EXPECTED_CONFIGS[device_type]
    cfg_conn._config_cleaner = getattr(helper, f"{device_type}_clean_response")

    yield cfg_conn
    if cfg_conn.conn.isalive():
        cfg_conn.close()


# scoping to function is probably dumb but dont have to screw around with which event loop is what this way
@pytest.fixture(scope="function")
async def async_conn(device_type, async_transport):
    device = DEVICES[device_type].copy()
    driver = device.pop("async_driver")
    device.pop("driver")

    port = device.pop("port")
    if async_transport in TELNET_TRANSPORTS:
        port = port + 1

    async_conn = driver(
        **device,
        port=port,
        transport=async_transport,
        timeout_socket=TIMEOUT_SOCKET,
        timeout_transport=TIMEOUT_TRANSPORT,
        timeout_ops=TIMEOUT_OPS,
    )
    return async_conn, device_type


@pytest.mark.asyncio
@pytest.fixture(scope="function")
async def async_cfg_conn(async_conn):
    scrapli_conn, device_type = async_conn
    async_cfg_conn = AsyncScrapliCfg(conn=scrapli_conn, platform=device_type)

    async_cfg_conn._expected_config = EXPECTED_CONFIGS[device_type]
    async_cfg_conn._config_cleaner = getattr(helper, f"{device_type}_clean_response")

    yield async_cfg_conn
    if async_cfg_conn.conn.isalive():
        await async_cfg_conn.close()
