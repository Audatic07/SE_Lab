# Lab 7 - Fuzz Testing the Spam Scoring Filter

SRN: **PES2UG24CS036**

Date: **8 November 2026**

Assigned repository: https://github.com/SETAPESU26/L6_L7_33_spam_scoring

Source directory: `lab7`

Baseline commit: `985be01d0936e946070685493cea685739decbfb`

Submission: https://github.com/Audatic07/SE_Lab/tree/main/Lab-7

## Required deliverables

1. [PDF report with screenshots](PES2UG24CS036_Lab7_FuzzTesting_Report.pdf)
2. [Fixed application](spam_scoring.py)
3. [Completed Hypothesis tests](test_spam_scoring.py)

The handout uses generic filenames `processor.py` and `test_processor.py`.
This assignment provides `spam_scoring.py` and `test_spam_scoring.py`; these names are preserved.
Only the Lab 7 exercise is included. The handout is not uploaded.

## Run

Use Python 3.11 or later for the pinned test dependencies. The recorded run used Python 3.13.15.
The application itself uses only the standard library.

```bash
cd Lab-7
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python spam_scoring.py
python -m pytest test_spam_scoring.py -v --hypothesis-show-statistics
```

The final run passed **72 tests**, including **13 Hypothesis properties**, each with
**500 successful generated examples** (6,500 successful examples in that full run),
and **59 deterministic regression cases**. No test is marked xfail or skipped.
`pytest.ini` excludes the intentionally broken original artifacts from normal discovery.

## Discovered failures and fixes

| Function | Minimized failing input | Original behavior | Fixed behavior |
| --- | --- | --- | --- |
| `sender_domain` | `None` | `AttributeError` | `""` |
| `sender_domain` | `""` | `IndexError` | `""` |
| `first_link` | `None` | `AttributeError` | `""` |
| `first_link` | `""` | `ValueError` | `""` |
| `shout_ratio` | `None` | `TypeError` | `0.0` |
| `shout_ratio` | `""` | `ZeroDivisionError` | `0.0` |

The mixed-type strategy also covers numbers, booleans, bytes, lists, dictionaries and
Unicode strings. Text-only strategies separately expose empty and missing-content failures.
The same six discovery test functions are retained unchanged in the final suite.
Generated valid addresses/URLs and an independent ratio reference prevent a constant
empty/zero implementation from passing.

### Function contracts

- `sender_domain(value)` accepts one simple email-like address, strips outer whitespace,
  requires one `@` and nonempty parts, rejects internal whitespace/control characters
  and malformed domain labels, and returns the lowercase domain. Otherwise it returns `""`.
  Unicode alphanumeric domain labels are accepted. This is a small extraction helper,
  not a complete RFC mailbox validator; it performs no DNS checks.
- `first_link(value)` returns the first HTTP(S) URL with a parseable hostname/port.
  It recognizes uppercase schemes, stops at Unicode whitespace or quotes/angle brackets,
  trims surrounding prose punctuation, preserves balanced parentheses and IPv6 brackets,
  and skips malformed candidates. Missing links and non-string inputs return `""`.
- `shout_ratio(value)` counts Unicode alphabetic characters, using uppercase letters as
  the numerator and all letters as the denominator. Nonletters do not affect the result.
  Non-string and letter-free values return `0.0`; all results lie in `[0.0, 1.0]`.

The valid CLI demonstration is byte-for-byte identical before and after the changes:
`deals.com`, `https://example.com/deal`, and `0.5833333333333334`.
Three blank CLI inputs now complete successfully instead of crashing at the first prompt.
Long-message and 100,000-trailing-bracket regression cases are included.

## Evidence

- `original/` preserves the assigned application, incomplete starter tests, and frozen
  six-test discovery suite. Failures in this directory are intentional.
- `evidence/logs/` contains unedited combined stdout/stderr for every recorded command,
  with JSON metadata for command, input, working directory, exit code, and UTC timestamp.
- `screenshots/` contains eight Chromium screenshots of those saved command outputs.
  These are browser captures of actual subprocess output, rather than native-terminal captures.
  The final full-suite screenshot is explicitly a final-14-line excerpt; the complete
  verbose output and Hypothesis statistics remain in the corresponding text log.
- `evidence/*.html` retains the exact evidence views used for screenshot capture.
- `evidence/manifest.json` records the source revision, tool versions, and SHA-256 hashes.

The original was run and fuzzed before editing the application. The six discovery
checks failed in two groups of three. After fixing the application, all six passed,
and the complete expanded suite passed all 72 cases.

To reproduce subprocess evidence from this folder:

```bash
python tools/run_evidence.py before
python tools/run_evidence.py after
```

The `before` command deliberately expects exit code 1 for the failing application and
fuzz tests; the normal original demonstration expects exit code 0. The `after` command
requires exit code 0 for every run. It does not modify application or test source files.

To recreate browser screenshots, make Playwright and Chromium available and run:

```bash
node tools/capture_evidence.cjs /absolute/path/to/chrome
```

To rebuild the PDF, install ReportLab and Pillow, then run `python tools/build_report.py`.
That script embeds Liberation Serif/Mono fonts from `/usr/share/fonts`; adjust those paths
when rebuilding on another operating system. These tools are not needed to run the app or tests.

Reference: [Hypothesis strategies](https://hypothesis.readthedocs.io/en/latest/reference/strategies.html)
and [settings and @given](https://hypothesis.readthedocs.io/en/latest/reference/api.html).
