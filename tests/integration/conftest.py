import pytest

from scrapli_cfg import AsyncScrapliCfg, ScrapliCfg

TIMEOUT_SOCKET = 60
TIMEOUT_TRANSPORT = 60
TIMEOUT_OPS = 60

TELNET_TRANSPORTS = (
    "telnet",
    "asynctelnet",
)


@pytest.fixture(
    scope="function",
    params=["cisco_iosxe", "cisco_nxos", "cisco_iosxr", "arista_eos", "juniper_junos"],
)
def device_type(request):
    yield request.param


@pytest.fixture(scope="function", params=["system", "paramiko", "telnet"])
def transport(request):
    yield request.param


@pytest.fixture(scope="function", params=["asyncssh", "asynctelnet"])
def async_transport(request):
    yield request.param


@pytest.fixture(scope="function")
def conn(test_devices_dict, device_type, transport):
    device = test_devices_dict[device_type].copy()
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
def cfg_conn(config_replacer_dict, conn, expected_configs):
    scrapli_conn, device_type = conn
    cfg_conn = ScrapliCfg(conn=scrapli_conn, dedicated_connection=True)

    cfg_conn._expected_config = expected_configs[device_type]
    cfg_conn._config_cleaner = config_replacer_dict[device_type]
    cfg_conn._load_config = "interface loopback1\ndescription tacocat"

    if device_type == "juniper_junos":
        cfg_conn._load_config = """interfaces {
        fxp0 {
            unit 0 {
                description RACECAR;
            }
        }
    }"""

    yield cfg_conn
    if cfg_conn.conn.isalive():
        cfg_conn.cleanup()


# scoping to function is probably dumb but dont have to screw around with which event loop is what this way
@pytest.fixture(scope="function")
async def async_conn(test_devices_dict, device_type, async_transport):
    device = test_devices_dict[device_type].copy()
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


@pytest.fixture(scope="function")
async def async_cfg_conn(config_replacer_dict, async_conn, expected_configs):
    scrapli_conn, device_type = async_conn
    async_cfg_conn = AsyncScrapliCfg(conn=scrapli_conn, dedicated_connection=True)

    async_cfg_conn._expected_config = expected_configs[device_type]
    async_cfg_conn._config_cleaner = config_replacer_dict[device_type]
    async_cfg_conn._load_config = "interface loopback1\ndescription tacocat"

    if device_type == "juniper_junos":
        async_cfg_conn._load_config = """interfaces {
    fxp0 {
        unit 0 {
            description RACECAR;
        }
    }
}"""

    yield async_cfg_conn
    if async_cfg_conn.conn.isalive():
        await async_cfg_conn.cleanup()
