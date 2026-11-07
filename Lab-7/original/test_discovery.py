"""Property-based input validation checks for all three assigned functions."""
from hypothesis import given, settings, strategies as st
from spam_scoring import sender_domain, first_link, shout_ratio


FUZZ = settings(max_examples=500, derandomize=True, database=None,
                report_multiple_bugs=False)
INPUTS = st.one_of(st.text(), st.none(), st.integers(), st.floats(),
                   st.binary(), st.booleans(), st.lists(st.integers(), max_size=10),
                   st.dictionaries(st.text(max_size=10), st.integers(), max_size=5))


@FUZZ
@given(INPUTS)
def test_sender_domain_no_crash(value):
    result = sender_domain(value)
    assert isinstance(result, str)
    assert result == result.lower()


@FUZZ
@given(INPUTS)
def test_first_link_no_crash(value):
    result = first_link(value)
    assert isinstance(result, str)
    assert not any(c.isspace() for c in result)


@FUZZ
@given(INPUTS)
def test_shout_ratio_no_crash(value):
    result = shout_ratio(value)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


@FUZZ
@given(st.text())
def test_sender_domain_text_no_crash(value):
    assert isinstance(sender_domain(value), str)


@FUZZ
@given(st.text())
def test_first_link_text_no_crash(value):
    assert isinstance(first_link(value), str)


@FUZZ
@given(st.text())
def test_shout_ratio_text_no_crash(value):
    assert 0.0 <= shout_ratio(value) <= 1.0
