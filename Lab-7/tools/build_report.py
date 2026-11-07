"""Build the Lab 7 report from the saved screenshots and actual run output."""
import hashlib
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                               Image, Table, TableStyle)

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '985be01d0936e946070685493cea685739decbfb'
for name, source in [
    ('LabSans', '/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf'),
    ('LabSans-Bold', '/usr/share/fonts/liberation-sans-fonts/LiberationSans-Bold.ttf'),
    ('LabMono', '/usr/share/fonts/liberation-mono-fonts/LiberationMono-Regular.ttf'),
]:
    pdfmetrics.registerFont(TTFont(name, source))
pdfmetrics.registerFontFamily('LabSans', normal='LabSans', bold='LabSans-Bold',
                              italic='LabSans', boldItalic='LabSans-Bold')
styles = getSampleStyleSheet()
for name, style in styles.byName.items():
    style.fontName = 'LabSans-Bold' if name.startswith('Heading') or name == 'Title' else 'LabSans'
styles['BodyText'].fontSize = 10
styles['BodyText'].leading = 14
styles['BodyText'].spaceAfter = 8
styles['Title'].fontSize = 25
styles['Title'].leading = 29
styles.add(ParagraphStyle('CaptionLab', parent=styles['BodyText'], fontSize=9, leading=12,
                         textColor=colors.HexColor('#425467')))
styles.add(ParagraphStyle('CommandLab', fontName='LabMono', fontSize=9, leading=13, spaceAfter=8))


def p(text, style='BodyText'):
    return Paragraph(escape(text).replace('\n', '<br/>'), styles[style])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('LabSans', 8)
    canvas.setFillColor(colors.HexColor('#526579'))
    canvas.drawString(40, 24, 'PES2UG24CS036 | Lab 7 Fuzz Testing | 8 November 2026')
    canvas.drawRightString(A4[0] - 40, 24, str(doc.page))
    canvas.restoreState()


def shot(story, stem, caption, height=600):
    path = ROOT / 'screenshots' / (stem + '.png')
    with PILImage.open(path) as im:
        width, original_height = im.size
    scale = min((A4[0] - 80) / width, height / original_height)
    story.extend([Image(str(path), width=width * scale, height=original_height * scale),
                  Spacer(1, 7), p(caption, 'CaptionLab')])


def make_table(rows, widths):
    data = [[p(str(value), 'CaptionLab') for value in row] for row in rows]
    table = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e9eef3')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d9d9d9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return table


def main():
    output = (ROOT / 'evidence/logs/07_after_full_suite.txt').read_text()
    counts = [int(n) for n in re.findall(r'(\d+) passing, 0 failing', output)]
    assert len(counts) == 13 and sum(counts) == 6500
    assert re.search(r'72 passed in [\d.]+s', output)
    assert (ROOT / 'evidence/logs/01_before_normal.txt').read_bytes() == (ROOT / 'evidence/logs/04_after_normal.txt').read_bytes()
    story = [p('Lab 7 Fuzz Testing', 'Title'), p('Spam Scoring Filter', 'Title'),
             Spacer(1, 10), p('SRN: PES2UG24CS036\nDate: 8 November 2026'),
             p('Assigned repository: https://github.com/SETAPESU26/L6_L7_33_spam_scoring', 'CaptionLab'),
             p('Source: lab7 | Baseline commit: ' + BASELINE, 'CaptionLab'),
             p('Result', 'Heading2'),
             p('All three input-validation functions are fixed. The six original discovery checks now pass. '
               'The expanded suite passes 72 tests, including 13 Hypothesis properties with 500 successful '
               'examples each: 6,500 successful generated examples in the final full run.'),
             p('Failures found before the fixes', 'Heading2')]
    story.append(make_table([
        ['Function', 'Fuzz input', 'Original failure', 'Fixed result'],
        ['sender_domain', 'None', 'AttributeError', 'empty string'],
        ['sender_domain', 'empty string', 'IndexError', 'empty string'],
        ['first_link', 'None', 'AttributeError', 'empty string'],
        ['first_link', 'empty string', 'ValueError', 'empty string'],
        ['shout_ratio', 'None', 'TypeError', '0.0'],
        ['shout_ratio', 'empty string', 'ZeroDivisionError', '0.0'],
    ], [119, 100, 151, A4[0] - 450]))
    story += [Spacer(1, 9), p('Method and submission mapping', 'Heading2'),
              p('The original application was executed, six discovery properties were written and failed '
                'against the original source, then the application was hardened and the same checks rerun. '
                'Additional properties and regression examples verify useful outputs as well as no-crash behavior.'),
              p('The handout names processor.py and test_processor.py generically. This assigned repository '
                'uses spam_scoring.py and test_spam_scoring.py; those filenames are preserved.'),
              p('Screenshots show real captured subprocess output displayed in Chromium. Logs and exit-code '
                'metadata are retained. The final full-suite screenshot is labeled as an excerpt; its complete '
                'output and statistics are included in evidence/logs/.', 'CaptionLab'),
              PageBreak(), p('Step 2 Run the original application', 'Heading1')]
    shot(story, '01_before_normal', 'A normal run succeeds: deals.com; https://example.com/deal; ratio 7/12. All three supplied inputs are recorded in the screenshot header.', 250)
    shot(story, '02_before_invalid', 'The same original program exits with code 1 on an empty email address. The traceback ends with IndexError, before the later prompts can run.', 330)
    story += [PageBreak(), p('Steps 3 and 4 Mixed input fuzzing fails', 'Heading1')]
    shot(story, '03_before_fuzz', 'Hypothesis minimizes each mixed-type failure to None: sender_domain raises AttributeError, first_link raises AttributeError, and shout_ratio raises TypeError. Three tests fail; three text-only tests are deselected.', 620)
    story += [PageBreak(), p('Steps 3 and 4 Text-only fuzzing fails', 'Heading1')]
    shot(story, '03b_before_text_fuzz', 'Text-only strategies independently minimize all three inputs to an empty string. They reveal IndexError, ValueError, and ZeroDivisionError respectively. These are genuine failed runs against the preserved original application.', 620)
    story += [PageBreak(), p('Step 5 Run the fixed application', 'Heading1')]
    shot(story, '04_after_normal', 'The normal demonstration is unchanged. Its complete output is byte-for-byte identical to the original normal-run log.', 250)
    shot(story, '05_after_invalid', 'Three blank inputs now finish with exit code 0. Sender domain and first link are empty strings; the uppercase ratio is 0.0. The application reaches all three prompts.', 250)
    story += [p('Input handling', 'Heading2'), p('Non-string inputs return safe empty/zero results. Addresses are checked before splitting; link searches tolerate missing or malformed URLs; the ratio checks its denominator before dividing.')]
    story += [PageBreak(), p('Step 6 Re-run the fuzz tests', 'Heading1')]
    shot(story, '06_after_discovery', 'All six original discovery properties pass against the fixed module; 66 additional cases are deselected for this direct comparison.', 170)
    shot(story, '07_after_full_suite', 'The final full suite passes 72 tests with exit code 0. This screenshot is explicitly the final 14 lines of the verbose output. All 13 properties report 500 passing generated examples in the complete text log.', 260)
    story += [p('Coverage beyond crash discovery', 'Heading2'),
              p('The final suite includes 59 deterministic regression cases and 13 generated properties. '
                'It checks correct domain extraction, invalid addresses, first-of-two link selection, '
                'Unicode whitespace, quoted links, punctuation, IPv6, malformed ports, Unicode case '
                'counting, numeric/container inputs, and 100,000-character inputs.'),
              p('A long unmatched-bracket URL test checks the linear trimming implementation. '
                'No test is skipped or marked as an expected failure. The fixed default pytest configuration '
                'excludes the intentionally broken original artifacts.')]
    story += [PageBreak(), p('Implementation and reproduction', 'Heading1'),
              p('sender_domain', 'Heading2'),
              p('Accept one simple email-like address with nonempty parts. Strip outer whitespace, reject '
                'internal whitespace/control characters and malformed labels, and lowercase the domain. '
                'This helper is not a full RFC mailbox validator and performs no network checks.'),
              p('first_link', 'Heading2'),
              p('Find HTTP(S) schemes case-insensitively; stop at whitespace, quotes or angle brackets. '
                'Remove prose punctuation while preserving balanced brackets, check the hostname/port, '
                'skip malformed candidates, and return the first acceptable URL.'),
              p('shout_ratio', 'Heading2'),
              p('Count Unicode alphabetic characters and uppercase alphabetic characters in one pass. '
                'Return uppercase/letters when letters exist; otherwise return 0.0. Nonletters do not '
                'change the ratio and all outputs are in [0.0, 1.0].'),
              p('Commands from Lab-7', 'Heading2'),
              p('python -m pip install -r requirements.txt\npython spam_scoring.py\npython -m pytest test_spam_scoring.py -v\npython tools/run_evidence.py before\npython tools/run_evidence.py after', 'CommandLab'),
              p('Environment: Python 3.13.15; Hypothesis 6.170.15; pytest 9.2.0. The pinned '
                'test dependencies require Python 3.11 or later. The application has no external runtime dependencies.'),
              p('Required deliverables', 'Heading2'),
              p('This screenshot PDF; spam_scoring.py; test_spam_scoring.py. Original files, '
                'test configuration, pinned dependencies, logs, screenshots and reproduction tools are also included.'),
              p('Submission: https://github.com/Audatic07/SE_Lab/tree/main/Lab-7', 'CaptionLab'),
              p('Reference: Hypothesis strategies and @given/settings API documentation at '
                'https://hypothesis.readthedocs.io/en/latest/reference/strategies.html and '
                'https://hypothesis.readthedocs.io/en/latest/reference/api.html', 'CaptionLab')]
    target = ROOT / 'PES2UG24CS036_Lab7_FuzzTesting_Report.pdf'
    SimpleDocTemplate(str(target), pagesize=A4, leftMargin=40, rightMargin=40,
                      topMargin=36, bottomMargin=44, title='Lab 7 Fuzz Testing Spam Scoring Filter',
                      author='PES2UG24CS036').build(story, onFirstPage=footer, onLaterPages=footer)
    manifest = {'srn': 'PES2UG24CS036', 'baseline_commit': BASELINE,
                'python': '3.13.15', 'hypothesis': '6.170.15', 'pytest': '9.2.0',
                'final_tests_passed': 72, 'hypothesis_properties': len(counts),
                'successful_generated_examples': sum(counts), 'sha256': {}}
    for file in sorted(ROOT.rglob('*')):
        if (not file.is_file() or any(part.startswith('.') or part == '__pycache__'
                                     for part in file.relative_to(ROOT).parts)
                or file.name == 'manifest.json'):
            continue
        manifest['sha256'][str(file.relative_to(ROOT))] = hashlib.sha256(file.read_bytes()).hexdigest()
    (ROOT / 'evidence/manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(target)


if __name__ == '__main__':
    main()
