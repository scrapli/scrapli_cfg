import pytest

from scrapli_cfg.exceptions import ScrapliCfgException, TemplateError


def test_response_obj_bool(response_obj):
    assert bool(response_obj) is True
    response_obj.failed = False
    assert bool(response_obj) is False


def test_response_obj_repr(response_obj):
    assert repr(response_obj) == "ScrapliCfgResponse <Success: False>"
    response_obj.failed = False
    assert repr(response_obj) == "ScrapliCfgResponse <Success: True>"


def test_response_obj_str(response_obj):
    assert str(response_obj) == "ScrapliCfgResponse <Success: False>"
    response_obj.failed = False
    assert str(response_obj) == "ScrapliCfgResponse <Success: True>"


def test_response_obj_raise_for_status(response_obj):
    with pytest.raises(ScrapliCfgException):
        response_obj.raise_for_status()

    response_obj.raise_for_status_exception = TemplateError

    with pytest.raises(TemplateError):
        response_obj.raise_for_status()
