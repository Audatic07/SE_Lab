"""Create the Lab 7 screenshot report from the recorded results."""
import hashlib
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape

from PIL import Image as PILImage
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '985be01d0936e946070685493cea685739decbfb'
for name, source in [
    ('LabSerif', '/usr/share/fonts/liberation-serif-fonts/LiberationSerif-Regular.ttf'),
    ('LabSerif-Bold', '/usr/share/fonts/liberation-serif-fonts/LiberationSerif-Bold.ttf'),
    ('LabMono', '/usr/share/fonts/liberation-mono-fonts/LiberationMono-Regular.ttf'),
]:
    pdfmetrics.registerFont(TTFont(name, source))
pdfmetrics.registerFontFamily('LabSerif', normal='LabSerif', bold='LabSerif-Bold',
                              italic='LabSerif', boldItalic='LabSerif-Bold')
styles = getSampleStyleSheet()
for name, style in styles.byName.items():
    style.fontName = 'LabSerif-Bold' if name.startswith('Heading') or name == 'Title' else 'LabSerif'
styles['BodyText'].fontSize = 12
styles['BodyText'].leading = 15
styles['BodyText'].spaceAfter = 8
styles['Title'].fontSize = 16
styles['Title'].leading = 20
styles['Title'].alignment = TA_CENTER
styles['Title'].spaceAfter = 14
styles['Heading1'].fontSize = 13
styles['Heading1'].leading = 16
styles['Heading1'].spaceAfter = 9
styles['Heading1'].spaceBefore = 6
styles.add(ParagraphStyle('CaptionLab', parent=styles['BodyText'], fontSize=11, leading=14))
styles.add(ParagraphStyle('CommandLab', fontName='LabMono', fontSize=10, leading=14, spaceAfter=9))


def p(text, style='BodyText'):
    return Paragraph(escape(text).replace('\n', '<br/>'), styles[style])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('LabSerif', 10)
    canvas.drawCentredString(A4[0] / 2, 24, str(doc.page))
    canvas.restoreState()


def shot(story, stem, caption, height=590):
    path = ROOT / 'screenshots' / (stem + '.png')
    with PILImage.open(path) as im:
        width, original_height = im.size
    scale = min((A4[0] - 90) / width, height / original_height)
    story.extend([Image(str(path), width=width * scale, height=original_height * scale),
                  Spacer(1, 6), p(caption, 'CaptionLab'), Spacer(1, 5)])


def main():
    output = (ROOT / 'evidence/logs/07_after_full_suite.txt').read_text()
    counts = [int(n) for n in re.findall(r'(\d+) passing, 0 failing', output)]
    assert len(counts) == 13 and sum(counts) == 6500
    assert re.search(r'72 passed in [\d.]+s', output)
    assert (ROOT / 'evidence/logs/01_before_normal.txt').read_bytes() == (ROOT / 'evidence/logs/04_after_normal.txt').read_bytes()

    story = [p('Lab 7 - Fuzz Testing', 'Title'),
             p('SRN: PES2UG24CS036\nDate: 8 November 2026'),
             p('Repository: https://github.com/SETAPESU26/L6_L7_33_spam_scoring', 'CaptionLab'),
             p('Aim', 'Heading1'),
             p('To use Hypothesis to find input validation bugs in the spam scoring program and fix them.'),
             p('1. Running the original program', 'Heading1'),
             p('python spam_scoring.py', 'CommandLab'),
             p('The sample inputs worked, but leaving the email blank caused an error.')]
    shot(story, '01_before_normal', 'Output with a valid email, a message containing a link, and normal text.', 170)
    shot(story, '02_before_invalid', 'A blank email caused IndexError because the code directly accessed the second part after splitting at @.', 220)

    story += [PageBreak(), p('2. Fuzz tests before fixing the code', 'Heading1'),
              p('The tests use @given to generate strings, None, numbers and other input types. '
                'The first run failed for all three functions with None as the input.'),
              p('python -m pytest test_discovery.py -q -k "not text_no_crash"', 'CommandLab')]
    shot(story, '03_before_fuzz',
         'sender_domain and first_link raised AttributeError. shout_ratio raised TypeError. The other three tests were not selected in this run.', 580)

    story += [PageBreak(), p('3. Testing empty strings', 'Heading1'),
              p('The text-only tests also failed. Hypothesis reduced the failing input to an empty string in all three cases.'),
              p('python -m pytest test_discovery.py -q -k text_no_crash', 'CommandLab')]
    shot(story, '03b_before_text_fuzz',
         'The errors were IndexError in sender_domain, ValueError in first_link, and ZeroDivisionError in shout_ratio.', 580)

    story += [PageBreak(), p('4. Fixing and running the program again', 'Heading1'),
              p('python spam_scoring.py', 'CommandLab')]
    shot(story, '04_after_normal', 'The valid sample inputs still gave the same output after the changes.', 190)
    shot(story, '05_after_invalid', 'With three blank inputs, the program now completes. It returns empty strings for the domain and link, and 0.0 for the ratio.', 190)
    story += [p('Changes made', 'Heading1'),
              p('sender_domain: Check the input type and address format before splitting it. Return an empty string if the address is invalid.'),
              p('first_link: Check for an HTTP or HTTPS link instead of assuming one exists. Return an empty string if there is no valid link.'),
              p('shout_ratio: Check whether any letters are present before dividing. Return 0.0 for empty input or text with no letters.')]

    story += [PageBreak(), p('5. Re-running the tests', 'Heading1'),
              p('The same six tests that failed earlier passed after the fixes.')]
    shot(story, '06_after_discovery', 'All six discovery tests passed. The additional tests were not selected in this run.', 135)
    story += [p('python -m pytest test_spam_scoring.py -v', 'CommandLab')]
    shot(story, '07_after_full_suite', 'Final test result: 72 passed. The screenshot shows the end of the full test output.', 240)
    story += [p('Result', 'Heading1'),
              p('All 72 tests passed. There are 13 Hypothesis tests with 500 generated examples each, and 59 fixed test cases. '
                'The extra cases check malformed addresses, missing links, Unicode text, whitespace and long inputs.'),
              p('The main issue was that the original functions assumed the input would always be valid. '
                'Fuzzing found failures with None and empty strings that the normal sample inputs did not show.'),
              p('The fixed code is in spam_scoring.py and the tests are in test_spam_scoring.py. '
                'The screenshots display saved command output in a browser. The full logs are in evidence/logs/.', 'CaptionLab'),
              p('Submission: https://github.com/Audatic07/SE_Lab/tree/main/Lab-7', 'CaptionLab')]

    target = ROOT / 'PES2UG24CS036_Lab7_FuzzTesting_Report.pdf'
    SimpleDocTemplate(str(target), pagesize=A4, leftMargin=45, rightMargin=45,
                      topMargin=40, bottomMargin=42, title='Lab 7 Fuzz Testing',
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
