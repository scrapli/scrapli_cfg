import pytest


@pytest.mark.asyncio
@pytest.mark.scrapli_replay
async def test_get_config(async_cfg_conn):
    await async_cfg_conn.open()
    config = await async_cfg_conn.get_config()
    assert config.failed is False
    # expected config is loaded from disk and set as an attribute in the fixture to make life easy
    assert async_cfg_conn._config_cleaner(config.result) == async_cfg_conn._config_cleaner(
        async_cfg_conn._expected_config
    )


@pytest.mark.asyncio
@pytest.mark.scrapli_replay
async def test_load_config_merge_diff_and_abort(async_cfg_conn):
    await async_cfg_conn.open()
    load_config = await async_cfg_conn.load_config(
        config="interface loopback1\ndescription tacocat", replace=False
    )
    assert load_config.failed is False
    diff_config = await async_cfg_conn.diff_config()
    assert diff_config.failed is False
    abort_config = await async_cfg_conn.abort_config()
    assert abort_config.failed is False
    # dont bother with checking the diff itself, we'll do that in unit tests much more thoroughly


@pytest.mark.asyncio
@pytest.mark.scrapli_replay
async def test_load_config_merge_diff_and_commit(async_cfg_conn):
    await async_cfg_conn.open()
    load_config = await async_cfg_conn.load_config(
        config=async_cfg_conn._expected_config, replace=True
    )
    assert load_config.failed is False
    diff_config = await async_cfg_conn.diff_config()
    assert diff_config.failed is False
    commit_config = await async_cfg_conn.commit_config()
    assert commit_config.failed is False
    # dont bother with checking the diff itself, we'll do that in unit tests much more thoroughly
