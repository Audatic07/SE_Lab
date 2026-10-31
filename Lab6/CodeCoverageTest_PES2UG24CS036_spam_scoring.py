"""Lab 6 code coverage tests. SRN: PES2UG24CS036.

Application: SETAPESU26/L6_L7_33_spam_scoring, lab6/spam_scoring.py.
Keep the application unchanged. From this folder, with the starter lab6
directory on PYTHONPATH, run:
    coverage run --source=spam_scoring -m pytest CodeCoverageTest_PES2UG24CS036_spam_scoring.py
    coverage report -m

These tests execute every application statement. The branch suite adds
decision outcomes and boundary cases that line coverage alone cannot prove.
"""

from spam_scoring import classify, filter_inbox, inbox_status, score_message


def test_plain_message_scores_zero():
    assert score_message("hello there", False, 0) == 0


def test_low_score_is_clean():
    assert classify(1) == "clean"


def test_spam_words_uppercase_and_many_links_accumulate():
    assert score_message("free winner prize urgent cash OFFER", False, 4) == 15


def test_few_links_add_one_point():
    assert score_message("ordinary message", False, 1) == 1


def test_known_sender_score_is_clamped_to_zero():
    assert score_message("hello", True, 0) == 0


def test_high_score_is_spam():
    assert classify(8) == "spam"


def test_medium_score_is_suspicious():
    assert classify(4) == "suspicious"


def test_filter_counts_all_three_labels():
    messages = [
        ("free winner prize urgent", False, 0),
        ("free winner", False, 0),
        ("hello", True, 0),
    ]
    assert filter_inbox(messages) == {"spam": 1, "suspicious": 1, "clean": 1}


def test_empty_inbox_status():
    assert inbox_status({"spam": 0, "suspicious": 0, "clean": 0}) == "empty"


def test_majority_spam_inbox_is_flooded():
    assert inbox_status({"spam": 2, "suspicious": 0, "clean": 1}) == "flooded"


def test_intermediate_spam_ratio_is_noisy():
    assert inbox_status({"spam": 1, "suspicious": 1, "clean": 1}) == "noisy"


def test_no_spam_inbox_is_healthy():
    assert inbox_status({"spam": 0, "suspicious": 0, "clean": 1}) == "healthy"
