"""Property-based input validation checks for all three assigned functions."""
from hypothesis import given, settings, strategies as st
import pytest
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


@pytest.mark.parametrize('value, expected', [
    ('offers@Deals.com', 'deals.com'), ('  a@EXAMPLE.COM  ', 'example.com'),
    ('first.last+tag@sub.Example.com', 'sub.example.com'), ('a@bücher.de', 'bücher.de'),
    ('', ''), ('plain-text', ''), ('@example.com', ''), ('a@', ''),
    ('a@@example.com', ''), ('a@b@c', ''), ('a b@example.com', ''),
    ('a@example.com/path', ''), ('a@.com', ''), ('a@bad..com', ''),
    ('a@-bad.com', ''), ('a@bad-.com', ''), ('a@bad_domain.com', ''),
    ('a\x00@example.com', ''), (None, ''), (42, ''),
])
def test_sender_domain_regressions(value, expected):
    assert sender_domain(value) == expected


@pytest.mark.parametrize('value, expected', [
    ('Visit https://example.com/deal now', 'https://example.com/deal'),
    ('https://example.com', 'https://example.com'),
    ('HTTPS://EXAMPLE.COM/path', 'HTTPS://EXAMPLE.COM/path'),
    ('one http://one.test/a two https://two.test/b', 'http://one.test/a'),
    ('Go https://example.com\nthen stop', 'https://example.com'),
    ('Go https://example.com\tthen stop', 'https://example.com'),
    ('Go https://example.com\u2003then stop', 'https://example.com'),
    ('See (https://example.com/a).', 'https://example.com/a'),
    ('See https://example.com/a(b).', 'https://example.com/a(b)'),
    ('<https://example.com/a>', 'https://example.com/a'),
    ('"https://example.com/a"', 'https://example.com/a'),
    ('http://[::1]:8080/a', 'http://[::1]:8080/a'),
    ('bad http://[bad good https://example.com', 'https://example.com'),
    ('bad http://host:99999 good https://example.com', 'https://example.com'),
    ('', ''), ('no links here', ''), ('http is not a URL', ''),
    ('http://', ''), ('https:///path', ''), ('ftp://example.com', ''),
    ('httpx://example.com', ''), ('http://host\x00', ''), (None, ''), (b'http://x.test', ''),
])
def test_first_link_regressions(value, expected):
    assert first_link(value) == expected


@pytest.mark.parametrize('value, expected', [
    ('', 0.0), ('123!? ', 0.0), ('🙂', 0.0), (None, 0.0), (42, 0.0),
    ('ABC', 1.0), ('abc', 0.0), ('AbC', 2 / 3),
    ('FREE prize NOW', 7 / 12), ('ÄäΩω', 0.5), ('你好', 0.0),
])
def test_shout_ratio_regressions(value, expected):
    assert shout_ratio(value) == pytest.approx(expected)


ASCII_LABEL = st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789', min_size=1, max_size=15)
LOCAL = st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789', min_size=1, max_size=20)


@FUZZ
@given(LOCAL, ASCII_LABEL, ASCII_LABEL)
def test_generated_valid_sender_domains(local, host, tld):
    domain = f'{host}.{tld}'
    assert sender_domain(f'  {local}@{domain.upper()}  ') == domain


@FUZZ
@given(st.text(alphabet=st.characters(blacklist_characters='@')))
def test_missing_at_is_invalid(value):
    assert sender_domain(value) == ''


@FUZZ
@given(LOCAL, ASCII_LABEL, LOCAL)
def test_multiple_at_is_invalid(left, host, right):
    assert sender_domain(f'{left}@{host}@{right}') == ''


@FUZZ
@given(ASCII_LABEL, LOCAL, st.sampled_from([' ', '\t', '\n', '\r', '\u2003']))
def test_generated_links_end_at_all_whitespace(host, path, separator):
    url = f'https://{host}.example/{path}'
    assert first_link(f'Visit {url}{separator}other text') == url


@FUZZ
@given(ASCII_LABEL, ASCII_LABEL)
def test_first_of_two_links_is_returned(first, second):
    url = f'http://{first}.example'
    assert first_link(f'{url} https://{second}.example') == url


@FUZZ
@given(st.text())
def test_shout_ratio_matches_reference(value):
    alphabetic = [c for c in value if c.isalpha()]
    expected = sum(c.isupper() for c in alphabetic) / len(alphabetic) if alphabetic else 0.0
    assert shout_ratio(value) == expected


@FUZZ
@given(st.text(), st.text(alphabet=' 1234567890!?\t\n🙂'))
def test_nonletters_do_not_change_shout_ratio(value, suffix):
    assert shout_ratio(value + suffix) == shout_ratio(value)


@pytest.mark.parametrize('function', [sender_domain, first_link, shout_ratio])
def test_large_input(function):
    # Exercise long hostile inputs without fragile wall-clock assertions.
    result = function('x' * 100_000)
    assert result == (0.0 if function is shout_ratio else '')


def test_many_unmatched_url_brackets():
    assert first_link('https://example.com/a' + ')' * 100_000) == 'https://example.com/a'
