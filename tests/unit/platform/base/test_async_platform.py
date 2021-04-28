import pytest

from scrapli_cfg.response import ScrapliCfgResponse


@pytest.mark.asyncio
async def test_open(async_cfg_object, monkeypatch):
    open_called = False
    get_version_called = False
    validate_and_set_version_called = False
    on_prepare_called = False

    # just going to mock things so we know that when open is called these functions get executed,
    # this test isn't for testing those other functions, we'll do that elsewhere

    async def _open(cls):
        nonlocal open_called
        open_called = True

    async def _get_version(cls):
        nonlocal get_version_called
        get_version_called = True

    def _validate_and_set_version(cls, version_response):
        nonlocal validate_and_set_version_called
        validate_and_set_version_called = True

    async def _on_prepare(cls):
        nonlocal on_prepare_called
        on_prepare_called = True

    monkeypatch.setattr("scrapli.driver.base.async_driver.AsyncDriver.open", _open)
    monkeypatch.setattr(
        "scrapli_cfg.platform.core.cisco_iosxe.async_platform.AsyncScrapliCfgIOSXE.get_version",
        _get_version,
    )
    monkeypatch.setattr(
        "scrapli_cfg.platform.core.cisco_iosxe.async_platform.AsyncScrapliCfgIOSXE._validate_and_set_version",
        _validate_and_set_version,
    )

    async_cfg_object.dedicated_connection = True
    async_cfg_object.on_prepare = _on_prepare
    await async_cfg_object.prepare()

    assert open_called is True
    assert get_version_called is True
    assert validate_and_set_version_called is True
    assert on_prepare_called is True


@pytest.mark.asyncio
async def test_close(async_cfg_object, monkeypatch):
    close_called = False

    # just going to mock things so we know that when open is called these functions get executed,
    # this test isn't for testing those other functions, we'll do that elsewhere

    async def _close(cls):
        nonlocal close_called
        close_called = True

    monkeypatch.setattr("scrapli.driver.base.async_driver.AsyncDriver.close", _close)
    # lie and pretend its alive so we actually run close
    monkeypatch.setattr("scrapli.driver.base.async_driver.AsyncDriver.isalive", lambda cls: True)

    async_cfg_object.dedicated_connection = True
    await async_cfg_object.cleanup()

    assert close_called is True


@pytest.mark.asyncio
async def test_context_manager(monkeypatch, async_cfg_object):
    """Asserts context manager properly opens/closes"""
    open_called = False
    close_called = False

    async def _prepare(cls):
        nonlocal open_called
        open_called = True

    async def _cleanup(cls):
        nonlocal close_called
        close_called = True

    monkeypatch.setattr(
        "scrapli_cfg.platform.base.async_platform.AsyncScrapliCfgPlatform.prepare", _prepare
    )
    monkeypatch.setattr(
        "scrapli_cfg.platform.base.async_platform.AsyncScrapliCfgPlatform.cleanup", _cleanup
    )

    async with async_cfg_object:
        pass

    assert open_called is True
    assert close_called is True


@pytest.mark.asyncio
async def test_render_substituted_config(monkeypatch, async_cfg_object):
    """Asserts context manager properly opens/closes"""
    get_config_called = False

    async def _get_config(cls, source):
        nonlocal get_config_called
        get_config_called = True
        response = ScrapliCfgResponse(host="localhost")
        response.result = "blah\nmatchthisline\nanotherblah"
        return response

    monkeypatch.setattr(
        "scrapli_cfg.platform.core.cisco_iosxe.async_platform.AsyncScrapliCfgIOSXE.get_config",
        _get_config,
    )

    rendered_config = await async_cfg_object.render_substituted_config(
        config_template="something\n{{ taco }}\nsomethingelse",
        substitutes=[("taco", "matchthisline")],
    )
    assert rendered_config == "something\nmatchthisline\nsomethingelse"
