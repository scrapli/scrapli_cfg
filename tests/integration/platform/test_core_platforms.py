import pytest


@pytest.mark.scrapli_replay
def test_get_config(cfg_conn):
    cfg_conn.open()
    config = cfg_conn.get_config()
    assert config.failed is False
    # expected config is loaded from disk and set as an attribute in the fixture to make life easy
    assert cfg_conn._config_cleaner(config.result) == cfg_conn._config_cleaner(
        cfg_conn._expected_config
    )


@pytest.mark.scrapli_replay
def test_load_config_merge_diff_and_abort(cfg_conn):
    cfg_conn.open()
    load_config = cfg_conn.load_config(config=cfg_conn._load_config, replace=False)
    assert load_config.failed is False
    diff_config = cfg_conn.diff_config()
    assert diff_config.failed is False
    abort_config = cfg_conn.abort_config()
    assert abort_config.failed is False
    # dont bother with checking the diff itself, we'll do that in unit tests much more thoroughly


@pytest.mark.scrapli_replay
def test_load_config_merge_diff_and_commit(cfg_conn):
    cfg_conn.open()
    load_config = cfg_conn.load_config(config=cfg_conn._expected_config, replace=True)
    assert load_config.failed is False
    diff_config = cfg_conn.diff_config()
    assert diff_config.failed is False
    commit_config = cfg_conn.commit_config()
    assert commit_config.failed is False
    # dont bother with checking the diff itself, we'll do that in unit tests much more thoroughly
