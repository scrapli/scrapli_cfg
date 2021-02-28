from pathlib import Path

import scrapli_cfg

EXPECTED_CONFIG_PATH = f"{Path(scrapli_cfg.__file__).parents[1]}/tests/expected_configs"
EXPECTED_CONFIGS = {
    "arista_eos": open(f"{EXPECTED_CONFIG_PATH}/arista_eos").read(),
    "cisco_iosxe": open(f"{EXPECTED_CONFIG_PATH}/cisco_iosxe").read(),
    "cisco_nxos": open(f"{EXPECTED_CONFIG_PATH}/cisco_nxos").read(),
    "cisco_iosxr": open(f"{EXPECTED_CONFIG_PATH}/cisco_iosxr").read(),
    # "juniper_junos": open(f"{EXPECTED_CONFIG_PATH}/juniper_junos")
}
