import pytest

from scrapli import AsyncScrapli, Scrapli
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.platform.base.sync_platform import ScrapliCfgBase


@pytest.fixture(scope="function")
def diff_obj():
    # setting width to 118 as thats what my console was for during testing, but of course if the
    # width is different for github actions or whoever this could change
    return ScrapliCfgDiffResponse(host="localhost", source="running", side_by_side_diff_width=118)


@pytest.fixture(scope="session", params=["cisco_iosxe", "cisco_iosxr", "cisco_nxos", "arista_eos"])
def sync_scrapli_conn(request):
    return Scrapli(host="localhost", platform=request.param)


@pytest.fixture(scope="session", params=["cisco_iosxe", "cisco_iosxr", "cisco_nxos", "arista_eos"])
def async_scrapli_conn(request):
    return AsyncScrapli(host="localhost", platform=request.param, transport="asyncssh")


@pytest.fixture(scope="function")
def base_cfg_object():
    base = ScrapliCfgBase
    base.conn = Scrapli(host="localhost", platform="cisco_iosxe")
    cfg_conn = ScrapliCfgBase(config_sources=["running", "startup"])
    return cfg_conn
