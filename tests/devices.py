import os

from helper import (
    arista_eos_clean_response,
    cisco_iosxe_clean_response,
    cisco_iosxr_clean_response,
    cisco_nxos_clean_response,
    juniper_junos_clean_response,
)

from scrapli.driver.core import (
    AsyncEOSDriver,
    AsyncIOSXEDriver,
    AsyncIOSXRDriver,
    AsyncJunosDriver,
    AsyncNXOSDriver,
    EOSDriver,
    IOSXEDriver,
    IOSXRDriver,
    JunosDriver,
    NXOSDriver,
)

VROUTER_MODE = bool(os.environ.get("SCRAPLI_VROUTER", False))

USERNAME = "vrnetlab"
PASSWORD = "VR-netlab9"

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
    "juniper_junos": {
        "driver": JunosDriver,
        "async_driver": AsyncJunosDriver,
        "auth_username": USERNAME,
        "auth_password": PASSWORD,
        "auth_secondary": PASSWORD,
        "auth_strict_key": False,
        "host": "localhost" if VROUTER_MODE else "172.18.0.15",
        "port": 25022 if VROUTER_MODE else 22,
    },
}

CONFIG_REPLACER = {
    "cisco_iosxe": cisco_iosxe_clean_response,
    "cisco_nxos": cisco_nxos_clean_response,
    "cisco_iosxr": cisco_iosxr_clean_response,
    "arista_eos": arista_eos_clean_response,
    "juniper_junos": juniper_junos_clean_response,
}
