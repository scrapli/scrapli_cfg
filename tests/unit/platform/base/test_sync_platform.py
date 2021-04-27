from scrapli_cfg.response import ScrapliCfgResponse


def test_open(sync_cfg_object, monkeypatch):
    open_called = False
    get_version_called = False
    validate_and_set_version_called = False
    on_prepare_called = False

    # just going to mock things so we know that when open is called these functions get executed,
    # this test isn't for testing those other functions, we'll do that elsewhere

    def _open(cls):
        nonlocal open_called
        open_called = True

    def _get_version(cls):
        nonlocal get_version_called
        get_version_called = True

    def _validate_and_set_version(cls, version_response):
        nonlocal validate_and_set_version_called
        validate_and_set_version_called = True

    def _on_prepare(cls):
        nonlocal on_prepare_called
        on_prepare_called = True

    monkeypatch.setattr("scrapli.driver.base.sync_driver.Driver.open", _open)
    monkeypatch.setattr(
        "scrapli_cfg.platform.core.cisco_iosxe.sync_platform.ScrapliCfgIOSXE.get_version",
        _get_version,
    )
    monkeypatch.setattr(
        "scrapli_cfg.platform.core.cisco_iosxe.sync_platform.ScrapliCfgIOSXE._validate_and_set_version",
        _validate_and_set_version,
    )

    sync_cfg_object.dedicated_connection = True
    sync_cfg_object.on_prepare = _on_prepare
    sync_cfg_object.prepare()

    assert open_called is True
    assert get_version_called is True
    assert validate_and_set_version_called is True
    assert on_prepare_called is True


def test_close(sync_cfg_object, monkeypatch):
    close_called = False

    # just going to mock things so we know that when open is called these functions get executed,
    # this test isn't for testing those other functions, we'll do that elsewhere

    def _close(cls):
        nonlocal close_called
        close_called = True

    monkeypatch.setattr("scrapli.driver.base.sync_driver.Driver.close", _close)
    # lie and pretend its alive so we actually run close
    monkeypatch.setattr("scrapli.driver.base.sync_driver.Driver.isalive", lambda cls: True)

    sync_cfg_object.dedicated_connection = True
    sync_cfg_object.cleanup()

    assert close_called is True


def test_context_manager(monkeypatch, sync_cfg_object):
    """Asserts context manager properly opens/closes"""
    open_called = False
    close_called = False

    def _prepare(cls):
        nonlocal open_called
        open_called = True

    def _cleanup(cls):
        nonlocal close_called
        close_called = True

    monkeypatch.setattr(
        "scrapli_cfg.platform.base.sync_platform.ScrapliCfgPlatform.prepare", _prepare
    )
    monkeypatch.setattr(
        "scrapli_cfg.platform.base.sync_platform.ScrapliCfgPlatform.cleanup", _cleanup
    )

    with sync_cfg_object:
        pass

    assert open_called is True
    assert close_called is True


def test_render_substituted_config(monkeypatch, sync_cfg_object):
    """Asserts context manager properly opens/closes"""
    get_config_called = False

    def _get_config(cls, source):
        nonlocal get_config_called
        get_config_called = True
        response = ScrapliCfgResponse(host="localhost")
        response.result = "blah\nmatchthisline\nanotherblah"
        return response

    monkeypatch.setattr(
        "scrapli_cfg.platform.core.cisco_iosxe.sync_platform.ScrapliCfgIOSXE.get_config",
        _get_config,
    )

    rendered_config = sync_cfg_object.render_substituted_config(
        config_template="something\n{{ taco }}\nsomethingelse",
        substitutes=[("taco", "matchthisline")],
    )
    assert rendered_config == "something\nmatchthisline\nsomethingelse"
