"""Lab 6 branch coverage tests. SRN: PES2UG24CS036.

Application: SETAPESU26/L6_L7_33_spam_scoring, lab6/spam_scoring.py.
Keep the application unchanged. From this folder, with the starter lab6
directory on PYTHONPATH, run:
    coverage run --branch --source=spam_scoring -m pytest BranchCoverageTest_PES2UG24CS036_spam_scoring.py
    coverage report -m

Tests cover every decision outcome, empty/nonempty loops, uppercase AND
conditions, sender adjustment, and both sides of each numeric threshold.
100% branch coverage does not imply every possible execution path is tested.
"""

import pytest

from spam_scoring import classify, filter_inbox, inbox_status, score_message


@pytest.mark.parametrize(
    "text,known,links,expected",
    [
        pytest.param("", False, 0, 0, id="empty-text-zero-links"),
        pytest.param("hello there", False, 0, 0, id="ordinary-words"),
        pytest.param("free", False, 0, 2, id="single-spam-word"),
        pytest.param("FREE! winner, prize. urgent cash", False, 0, 10,
                     id="all-spam-words-case-and-punctuation"),
        pytest.param("prize prize", False, 0, 4, id="repeated-spam-word"),
        pytest.param("SALE", False, 0, 1, id="uppercase-length-four"),
        pytest.param("BUY", False, 0, 0, id="uppercase-length-three"),
        pytest.param("Offer", False, 0, 0, id="long-word-not-uppercase"),
        pytest.param("1234", False, 0, 0, id="digits-not-uppercase"),
        pytest.param("FREE", False, 0, 2, id="spam-rule-precedes-uppercase"),
        pytest.param("", False, 1, 1, id="first-link"),
        pytest.param("", False, 3, 1, id="three-link-boundary"),
        pytest.param("", False, 4, 4, id="four-link-boundary"),
        pytest.param("", True, 0, 0, id="known-sender-negative-clamped"),
        pytest.param("free", True, 0, 0, id="known-sender-two-clamped"),
        pytest.param("free", True, 1, 0, id="known-sender-exact-zero"),
        pytest.param("free winner", True, 0, 1, id="known-sender-positive"),
        pytest.param("", True, 4, 1, id="known-sender-link-adjustment"),
        pytest.param("free OFFER", False, 1, 4, id="combined-signals"),
        pytest.param("free winner prize urgent cash OFFER", False, 4, 15,
                     id="all-signals-accumulate"),
    ],
)
def test_scoring_rules_and_boundaries(text, known, links, expected):
    assert score_message(text, known, links) == expected


@pytest.mark.parametrize(
    "score,expected",
    [(0, "clean"), (3, "clean"), (4, "suspicious"),
     (7, "suspicious"), (8, "spam"), (100, "spam")],
)
def test_classification_boundaries(score, expected):
    assert classify(score) == expected


@pytest.mark.parametrize(
    "messages,expected",
    [
        pytest.param([], {"spam": 0, "suspicious": 0, "clean": 0},
                     id="empty-inbox-loop-skipped"),
        pytest.param([("hello", False, 0)],
                     {"spam": 0, "suspicious": 0, "clean": 1},
                     id="single-clean-message"),
        pytest.param([
            ("free winner prize urgent", False, 0),
            ("free winner", False, 0),
            ("hello", True, 0),
        ], {"spam": 1, "suspicious": 1, "clean": 1}, id="each-label"),
        pytest.param([
            ("free winner prize urgent", False, 0),
            ("free winner prize urgent", False, 0),
        ], {"spam": 2, "suspicious": 0, "clean": 0}, id="repeat-counting"),
        pytest.param([("free winner prize urgent", True, 0)],
                     {"spam": 0, "suspicious": 1, "clean": 0},
                     id="known-sender-changes-classification"),
    ],
)
def test_filter_inbox_counts(messages, expected):
    assert filter_inbox(messages) == expected


@pytest.mark.parametrize(
    "counts,expected",
    [
        pytest.param({"spam": 0, "suspicious": 0, "clean": 0}, "empty",
                     id="zero-total-early-return"),
        pytest.param({"spam": 0, "suspicious": 0, "clean": 10}, "healthy",
                     id="zero-spam-ratio"),
        pytest.param({"spam": 1, "suspicious": 0, "clean": 9}, "healthy",
                     id="below-twenty-percent"),
        pytest.param({"spam": 2, "suspicious": 3, "clean": 5}, "healthy",
                     id="exactly-twenty-percent"),
        pytest.param({"spam": 3, "suspicious": 0, "clean": 7}, "noisy",
                     id="above-twenty-percent"),
        pytest.param({"spam": 5, "suspicious": 0, "clean": 5}, "noisy",
                     id="exactly-fifty-percent"),
        pytest.param({"spam": 6, "suspicious": 0, "clean": 4}, "flooded",
                     id="above-fifty-percent"),
        pytest.param({"spam": 10, "suspicious": 0, "clean": 0}, "flooded",
                     id="all-spam"),
        pytest.param({"spam": 0, "suspicious": 10, "clean": 0}, "healthy",
                     id="suspicious-included-in-total"),
    ],
)
def test_inbox_status_boundaries(counts, expected):
    assert inbox_status(counts) == expected


def test_complete_inbox_pipeline():
    messages = [
        ("free winner prize urgent", False, 0),
        ("cash prize winner urgent", False, 0),
        ("free winner", False, 0),
        ("hello", True, 0),
    ]
    counts = filter_inbox(messages)
    assert counts == {"spam": 2, "suspicious": 1, "clean": 1}
    assert inbox_status(counts) == "noisy"
