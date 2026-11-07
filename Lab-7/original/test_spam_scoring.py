from hypothesis import given, strategies as st
from spam_scoring import sender_domain, first_link, shout_ratio

@given(st.text() | st.none())
def test_sender_domain_no_crash(s):

@given(st.text() | st.none())
def test_first_link_no_crash(s):

@given(st.text() | st.none())
def test_shout_ratio_no_crash(s):
