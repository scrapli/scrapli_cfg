import pytest

from scrapli.response import Response
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.exceptions import (
    AbortConfigError,
    CommitConfigError,
    DiffConfigError,
    InvalidConfigTarget,
    TemplateError,
    VersionError,
)
from scrapli_cfg.response import ScrapliCfgResponse


def test_render_substituted_config(base_cfg_object):
    result = base_cfg_object._render_substituted_config(
        config_template="notinthesource\n{{ taco }}\nalsonotinthesource",
        substitutes=[("taco", "yoinkthisline")],
        source_config="something\nyoinkthisline\nsomethingelse",
    )
    assert result == "notinthesource\nyoinkthisline\nalsonotinthesource"


def test_render_substituted_config_no_substitutes(base_cfg_object):
    with pytest.raises(TemplateError):
        base_cfg_object._render_substituted_config(
            config_template="", substitutes=[], source_config=""
        )


def test_render_substituted_config_incorrect_substitutes(base_cfg_object):
    with pytest.raises(TemplateError):
        base_cfg_object._render_substituted_config(
            config_template="{{ taco }}", substitutes=[("racecar", "")], source_config=""
        )


def test_render_substituted_config_pattern_not_in_source(base_cfg_object):
    with pytest.raises(TemplateError):
        base_cfg_object._render_substituted_config(
            config_template="notinthesource\n{{ taco }}\nalsonotinthesource",
            substitutes=[("taco", "yoinkthisline")],
            source_config="something\nNOPE\nsomethingelse",
        )


def test_validate_and_set_version(base_cfg_object):
    assert base_cfg_object._version_string == ""
    version_response = ScrapliCfgResponse(host="localhost")
    version_response.record_response(scrapli_responses=[], result="1.2.3")
    base_cfg_object._validate_and_set_version(version_response=version_response)
    assert base_cfg_object._version_string == "1.2.3"


def test_validate_and_set_version_failed(base_cfg_object):
    failed_version_response = ScrapliCfgResponse(host="localhost")
    with pytest.raises(VersionError):
        base_cfg_object._validate_and_set_version(version_response=failed_version_response)


def test_validate_and_set_version_failed_to_parse(base_cfg_object):
    failed_to_parse_version_response = ScrapliCfgResponse(host="localhost")
    failed_to_parse_version_response.record_response(scrapli_responses=[], result="")
    with pytest.raises(VersionError):
        base_cfg_object._validate_and_set_version(version_response=failed_to_parse_version_response)


def test_pre_get_version(base_cfg_object):
    r = base_cfg_object._pre_get_version()
    assert isinstance(r, ScrapliCfgResponse)


def test_post_get_version(base_cfg_object):
    # send a failed response so we also cover the logger message indicating that there was a fail
    get_version_response = ScrapliCfgResponse(host="localhost")
    scrapli_response = Response(host="localhost", channel_input="show version")
    post_get_version_response = base_cfg_object._post_get_version(
        response=get_version_response, scrapli_responses=[scrapli_response], result="blah"
    )
    assert post_get_version_response.failed is True
    assert post_get_version_response.result == "blah"


def test_pre_get_config(base_cfg_object):
    r = base_cfg_object._pre_get_config(source="running")
    assert isinstance(r, ScrapliCfgResponse)


def test_pre_get_config_exception(base_cfg_object):
    with pytest.raises(InvalidConfigTarget):
        base_cfg_object._pre_get_config(source="tacocat")


def test_post_get_config(base_cfg_object):
    # send a failed response so we also cover the logger message indicating that there was a fail
    get_config_response = ScrapliCfgResponse(host="localhost")
    scrapli_response = Response(host="localhost", channel_input="show version")
    post_get_config_response = base_cfg_object._post_get_config(
        response=get_config_response,
        scrapli_responses=[scrapli_response],
        result="blah",
        source="running",
    )
    assert post_get_config_response.failed is True
    assert post_get_config_response.result == "blah"


def test_pre_load_config(base_cfg_object):
    r = base_cfg_object._pre_load_config(config="newconfig")
    assert base_cfg_object.candidate_config == "newconfig"
    assert isinstance(r, ScrapliCfgResponse)


def test_post_load_config(base_cfg_object):
    # send a failed response so we also cover the logger message indicating that there was a fail
    load_config_response = ScrapliCfgResponse(host="localhost")
    scrapli_response = Response(host="localhost", channel_input="load a config")
    post_load_config_response = base_cfg_object._post_load_config(
        response=load_config_response, scrapli_responses=[scrapli_response]
    )
    assert post_load_config_response.failed is True


def test_pre_abort_config(base_cfg_object):
    r = base_cfg_object._pre_abort_config(session_or_config_file=True)
    assert isinstance(r, ScrapliCfgResponse)


def test_pre_abort_config_exception(base_cfg_object):
    with pytest.raises(AbortConfigError):
        base_cfg_object._pre_abort_config(session_or_config_file=False)


def test_post_abort_config(base_cfg_object):
    # send a failed response so we also cover the logger message indicating that there was a fail
    abort_config_response = ScrapliCfgResponse(host="localhost")
    scrapli_response = Response(host="localhost", channel_input="abort a config")
    post_abort_config_response = base_cfg_object._post_abort_config(
        response=abort_config_response, scrapli_responses=[scrapli_response]
    )
    assert post_abort_config_response.failed is True


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
    # send a failed response so we also cover the logger message indicating that there was a fail
    commit_config_response = ScrapliCfgResponse(host="localhost")
    scrapli_response = Response(host="localhost", channel_input="commit a config")
    post_commit_config_response = base_cfg_object._post_commit_config(
        response=commit_config_response, scrapli_responses=[scrapli_response]
    )
    assert post_commit_config_response.failed is True


def test_pre_diff_config(base_cfg_object):
    r = base_cfg_object._pre_diff_config(source="running", session_or_config_file=True)
    assert isinstance(r, ScrapliCfgResponse)


def test_pre_diff_config_exception_invalid_target(base_cfg_object):
    with pytest.raises(InvalidConfigTarget):
        base_cfg_object._pre_diff_config(source="tacocat", session_or_config_file=True)


def test_pre_diff_config_exception_no_session_or_config(base_cfg_object):
    with pytest.raises(DiffConfigError):
        base_cfg_object._pre_diff_config(source="running", session_or_config_file=False)


def test_post_diff_config(diff_obj, base_cfg_object):
    scrapli_response = Response(host="localhost", channel_input="diff a config")
    source_config = "source config"
    candidate_config = "candidate config"
    device_diff = "they different yo"
    post_diff_response = base_cfg_object._post_diff_config(
        diff_response=diff_obj,
        scrapli_responses=[scrapli_response],
        source_config=source_config,
        candidate_config=candidate_config,
        device_diff=device_diff,
    )
    assert post_diff_response.failed is True
