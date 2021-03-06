import pytest

from scrapli_cfg.exceptions import (
    AbortConfigError,
    CommitConfigError,
    DiffConfigError,
    InvalidConfigTarget,
)
from scrapli_cfg.response import ScrapliCfgResponse


def test_render_substituted_config(base_cfg_object):
    pass


def test_validate_and_set_version(base_cfg_object):
    pass


def test_pre_get_version(base_cfg_object):
    r = base_cfg_object._pre_get_version()
    assert isinstance(r, ScrapliCfgResponse)


def test_post_get_version(base_cfg_object):
    pass


def test_pre_get_config(base_cfg_object):
    r = base_cfg_object._pre_get_config(source="running")
    assert isinstance(r, ScrapliCfgResponse)


def test_pre_get_config_exception(base_cfg_object):
    with pytest.raises(InvalidConfigTarget):
        base_cfg_object._pre_get_config(source="tacocat")


def test_post_get_config(base_cfg_object):
    pass


def test_pre_load_config(base_cfg_object):
    r = base_cfg_object._pre_load_config(config="newconfig")
    assert base_cfg_object.candidate_config == "newconfig"
    assert isinstance(r, ScrapliCfgResponse)


def test_post_load_config(base_cfg_object):
    pass


def test_pre_abort_config(base_cfg_object):
    r = base_cfg_object._pre_abort_config(session_or_config_file=True)
    assert isinstance(r, ScrapliCfgResponse)


def test_pre_abort_config_exception(base_cfg_object):
    with pytest.raises(AbortConfigError):
        base_cfg_object._pre_abort_config(session_or_config_file=False)


def test_post_abort_config(base_cfg_object):
    pass


def test_pre_commit_config(base_cfg_object):
    r = base_cfg_object._pre_commit_config(source="running", session_or_config_file=True)
    assert isinstance(r, ScrapliCfgResponse)


def test_pre_commit_config_exception_invalid_target(base_cfg_object):
    with pytest.raises(InvalidConfigTarget):
        base_cfg_object._pre_commit_config(source="tacocat", session_or_config_file=True)


def test_pre_commit_config_exception_no_session_or_config(base_cfg_object):
    with pytest.raises(CommitConfigError):
        base_cfg_object._pre_commit_config(source="running", session_or_config_file=False)


def test_post_commit_config(base_cfg_object):
    pass


def test_pre_diff_config(base_cfg_object):
    r = base_cfg_object._pre_diff_config(source="running", session_or_config_file=True)
    assert isinstance(r, ScrapliCfgResponse)


def test_pre_diff_config_exception_invalid_target(base_cfg_object):
    with pytest.raises(InvalidConfigTarget):
        base_cfg_object._pre_diff_config(source="tacocat", session_or_config_file=True)


def test_pre_diff_config_exception_no_session_or_config(base_cfg_object):
    with pytest.raises(DiffConfigError):
        base_cfg_object._pre_diff_config(source="running", session_or_config_file=False)


def test_post_diff_config(base_cfg_object):
    pass
