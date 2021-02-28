import pytest


@pytest.mark.scrapli_replay
def test_get_config(cfg_conn):
    cfg_conn.open()
    config = cfg_conn.get_config()
    assert config.failed is False
    # expected config is loaded from disk and set as an attribute in the fixture to make life easy
    assert cfg_conn._config_cleaner(config.result) == cfg_conn._expected_config
