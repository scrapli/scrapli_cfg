import pytest

from scrapli_cfg.diff import END_COLOR, GREEN, RED, YELLOW

DUMMY_SOURCE_CONFIG = """!
interface loopback123
   description tacocat
!
"""

DUMMY_CANDIDATE_CONFIG = """!
interface loopback456
   description racecar
!
"""

DUMMY_DEVICE_DIFF = """!List of Commands:
interface loopback456
   description racecar
end"""

COLORIZED_SIDE_BY_SIDE_DIFF = "!                                                          !\n\x1b[91minterface loopback123                                      \x1b[0m\n                  ^^^                                                        ^^^\n                                                           \x1b[92minterface loopback456\x1b[0m\n                  ^^^                                                        ^^^\n\x1b[91m   description tacocat                                     \x1b[0m\n               ^  ^  ^                                                    ^  ^  ^\n                                                           \x1b[92m   description racecar\x1b[0m\n               ^  ^  ^                                                    ^  ^  ^\n!                                                          !"
SIDE_BY_SIDE_DIFF = "!                                                          !\n- interface loopback123                                      \n                  ^^^                                                        ^^^\n                                                           + interface loopback456\n                  ^^^                                                        ^^^\n-    description tacocat                                     \n               ^  ^  ^                                                    ^  ^  ^\n                                                           +    description racecar\n               ^  ^  ^                                                    ^  ^  ^\n!                                                          !"
COLORIZED_UNIFIED_DIFF = "!\n\x1b[91minterface loopback123\n\x1b[0m                  ^^^\n\x1b[92minterface loopback456\n\x1b[0m                  ^^^\n\x1b[91m   description tacocat\n\x1b[0m               ^  ^  ^\n\x1b[92m   description racecar\n\x1b[0m               ^  ^  ^\n!\n"
UNIFIED_DIFF = "!\n- interface loopback123\n                  ^^^\n+ interface loopback456\n                  ^^^\n-    description tacocat\n               ^  ^  ^\n+    description racecar\n               ^  ^  ^\n!\n"


def test_record_diff_response(diff_obj):
    assert diff_obj.colorize is True
    assert diff_obj.side_by_side_diff_width == 118
    assert diff_obj.source == "running"
    assert diff_obj.source_config == ""
    assert diff_obj.candidate_config == ""
    assert diff_obj.device_diff == ""

    diff_obj.record_diff_response(
        source_config=DUMMY_SOURCE_CONFIG,
        candidate_config=DUMMY_CANDIDATE_CONFIG,
        device_diff=DUMMY_DEVICE_DIFF,
    )

    assert diff_obj._difflines == [
        "  !\n",
        "- interface loopback123\n",
        "?                   ^^^\n",
        "+ interface loopback456\n",
        "?                   ^^^\n",
        "-    description tacocat\n",
        "?                ^  ^  ^\n",
        "+    description racecar\n",
        "?                ^  ^  ^\n",
        "  !\n",
    ]
    assert diff_obj.subtractions == "interface loopback123\n   description tacocat\n"
    assert diff_obj.additions == "interface loopback456\n   description racecar\n"
    assert diff_obj.device_diff == DUMMY_DEVICE_DIFF


@pytest.mark.parametrize(
    "colorize",
    (
        True,
        False,
    ),
    ids=("color", "no color"),
)
def test_generate_colors(diff_obj, colorize):
    diff_obj.colorize = colorize
    colors = diff_obj._generate_colors()

    if colorize is True:
        assert colors == (YELLOW, RED, GREEN, END_COLOR)
    else:
        assert colors == ("? ", "- ", "+ ", "")


@pytest.mark.parametrize(
    "colorize",
    (
        True,
        False,
    ),
    ids=("color", "no color"),
)
def test_side_by_side_diff(diff_obj, colorize):
    diff_obj.colorize = colorize
    assert diff_obj.side_by_side_diff == ""

    diff_obj.record_diff_response(
        source_config=DUMMY_SOURCE_CONFIG,
        candidate_config=DUMMY_CANDIDATE_CONFIG,
        device_diff=DUMMY_DEVICE_DIFF,
    )

    if colorize is True:
        assert diff_obj.side_by_side_diff == COLORIZED_SIDE_BY_SIDE_DIFF
    else:
        assert diff_obj.side_by_side_diff == SIDE_BY_SIDE_DIFF


@pytest.mark.parametrize(
    "colorize",
    (
        True,
        False,
    ),
    ids=("color", "no color"),
)
def test_unified_diff(diff_obj, colorize):
    diff_obj.colorize = colorize
    assert diff_obj.side_by_side_diff == ""

    diff_obj.record_diff_response(
        source_config=DUMMY_SOURCE_CONFIG,
        candidate_config=DUMMY_CANDIDATE_CONFIG,
        device_diff=DUMMY_DEVICE_DIFF,
    )

    if colorize is True:
        assert diff_obj.unified_diff == COLORIZED_UNIFIED_DIFF
    else:
        assert diff_obj.unified_diff == UNIFIED_DIFF
