"""Build the screenshot report and a faithful visible-message chat export.

Requires reportlab (only for rebuilding PDFs). Supply the local Codex JSONL session
with --session to refresh the chat; otherwise the saved Markdown is reused.
"""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                               PageBreak, Preformatted, KeepTogether)

ROOT = Path(__file__).resolve().parents[1]
SRN = "PES2UG24CS036"
# Embed fonts so the PDFs render reliably without host font substitution.
# These fonts ship with many Linux systems; adjust the paths when rebuilding elsewhere.
FONT_DIR = Path("/usr/share/fonts/liberation-sans-fonts")
pdfmetrics.registerFont(TTFont("LabSans", str(FONT_DIR / "LiberationSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("LabSans-Bold", str(FONT_DIR / "LiberationSans-Bold.ttf")))
pdfmetrics.registerFontFamily("LabSans", normal="LabSans", bold="LabSans-Bold",
                              italic="LabSans", boldItalic="LabSans-Bold")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle("Deck", fontName="Helvetica", fontSize=12, leading=18,
                         textColor=colors.HexColor("#42556b"), spaceAfter=14))
styles.add(ParagraphStyle("CaptionText", fontName="Helvetica", fontSize=9, leading=12,
                         spaceAfter=10, textColor=colors.HexColor("#42556b")))
styles.add(ParagraphStyle("ChatText", fontName="Helvetica", fontSize=10, leading=15,
                         spaceAfter=9, splitLongWords=True))
styles.add(ParagraphStyle("ReportTitle", parent=styles["Title"], alignment=TA_CENTER,
                         fontSize=26, leading=31, textColor=colors.HexColor("#123757")))
for name, style in styles.byName.items():
    style.fontName = "LabSans-Bold" if name.startswith("Heading") or name in {"Title", "ReportTitle"} else "LabSans"


def para(text, style="BodyText"):
    return Paragraph(escape(text).replace("\n", "<br/>"), styles[style])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d0dae3"))
    canvas.line(42, 38, A4[0] - 42, 38)
    canvas.setFont("LabSans", 8)
    canvas.setFillColor(colors.HexColor("#536679"))
    canvas.drawString(42, 25, f"{SRN} | Lab 4: VibeCoding | 16 October 2026")
    canvas.drawRightString(A4[0] - 42, 25, str(doc.page))
    canvas.restoreState()


def build(path, story):
    doc = SimpleDocTemplate(str(path), pagesize=A4, topMargin=42, bottomMargin=50,
                            leftMargin=42, rightMargin=42,
                            title=path.stem.replace("_", " "), author=SRN)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def screenshot(story, filename, caption):
    story.append(KeepTogether([Image(str(ROOT / "screenshots" / filename), width=400, height=300),
                              Spacer(1, 4), para(caption, "CaptionText")]))


def report():
    story = [Spacer(1, 30), para("Missile Command", "ReportTitle"),
             para("Lab 4 - VibeCoding", "ReportTitle"),
             Spacer(1, 15), para(f"SRN: {SRN}\n16 October 2026", "Deck"),
             para("Assigned repository", "Heading2"),
             para("https://github.com/SETAPESU26/33_missileCommand"),
             para("Baseline: b4318a97def23a2fe945a9a78f713c83ebf6990f", "CaptionText"),
             para("Completed work", "Heading2")]
    for text in [
        "1. Battery selection filters out destroyed and empty batteries, selects the nearest usable battery, and handles no available battery safely.",
        "2. Explosion colors smoothly change from white through yellow and orange to dark red over their lifetime.",
        "3. City destruction displays a three-second warning. When two or fewer cities survive, the message becomes critical.",
        "4. Every newly crossed 2,000-point milestone rebuilds one destroyed city, with a rebuild message and next-milestone display.",
        "Supporting fixes ensure exact interceptor arrival, prevent waves from clearing flying interceptors, and reject expired blast collisions."]:
        story += [para(text), Spacer(1, 7)]
    story += [para("Evidence and verification", "Heading2"),
              para("26 regression tests passed. Ten unedited Pygame surface screenshots are included. "
                   "Screenshots replace videos at the student's explicit request."),
              Spacer(1, 8),
              para("Screenshots use deterministic staged scenarios. Missile positions, explosion ages and the repair starting score are configured by the capture script; "
                   "the game itself renders every image and performs the launches, impacts and repair collision. These are not an uninterrupted manual gameplay recording.", "CaptionText"),
              para("AI assistance is disclosed in the accompanying actual-message chat export. No separate student prompts have been invented.", "CaptionText")]
    pages = [
        ("Battery selection: before and after", [
            ("before_02_battery_fallback.png", "Before: ten launches exhaust the left battery. A further click at (70,180) produces no interceptor; the other batteries retain 10 rounds each."),
            ("after_02_battery_fallback.png", "After: the same click launches from the middle battery. Its ammunition falls to 9; the cyan interceptor trail and target ring are visible.")]),
        ("Explosion colors and destruction warning", [
            ("after_03_explosion_colors.png", "Four explosions at progress 0.12, 0.38, 0.62 and 0.85 show the white/yellow-to-red lifetime gradient. These are staged explosion ages."),
            ("after_04_city_warning.png", "Four actual impact() calls destroy four cities. The HUD shows Cities 2/6 and the critical warning appears for three seconds.")]),
        ("Score-based city repair", [
            ("after_05_before_repair.png", "Before repair: one city is destroyed and the scenario starts at 1,975 points. The city count is 5/6 and the next threshold is 2,000."),
            ("after_06_city_repaired.png", "An explosion intercepts a missile for 25 points. At 2,000 points the destroyed city is rebuilt, the count becomes 6/6 and the next threshold is 4,000.")]),
        ("Game over and reset", [
            ("after_07_game_over.png", "All six cities are destroyed by impacts. The game enters the lose state and displays ALL CITIES LOST - Press R."),
            ("after_08_reset.png", "Reset returns to score 0, wave 1, all six cities, three full batteries and the first repair milestone. R-key event dispatch is also tested.")])]
    for title, shots in pages:
        story += [PageBreak(), para(title, "Heading1")]
        for filename, caption in shots:
            screenshot(story, filename, caption)
    story += [PageBreak(), para("Validation and reproduction", "Heading1"),
              para("Environment: Python 3.13.15; Pygame 2.6.1; SDL dummy video/audio drivers for automated verification."),
              para("Run the game", "Heading2"),
              Preformatted("cd Lab-4\npython -m pip install -r requirements.txt\npython game.py", styles["Code"]),
              para("Click above the ground to fire; R resets; close the window to quit."),
              para("Run checks and recapture screenshots", "Heading2"),
              Preformatted("python -m unittest discover -s tests -v\npython tools/capture_screenshots.py --phase after", styles["Code"]),
              para("Checks completed", "Heading2")]
    checks = ["Nearest available battery, depleted/destroyed fallback, mixed unavailability and safe no-ammo behavior.",
              "Exact interceptor arrival, short remaining distances, zero-distance targets and target-centered detonation.",
              "Valid interpolated colors; destruction hook runs once per city; battery impacts skip the hook; alerts expire.",
              "Repair threshold, no repeated award, multiple crossed milestones, no banked repairs and disabled repairs.",
              "Explosion radius/boundary collision, overlapping blast scoring and expired explosion cleanup.",
              "Missile impact, valid spawn targets, wave completion, ammunition replenishment, loss and full reset.",
              "Main-loop dispatch of mouse click, R key and quit events."]
    for text in checks:
        story += [para(text), Spacer(1, 8)]
    story += [para("Result: 26 tests passed; exit code 0.", "Heading2"),
              para("Full output: verification.txt. Screenshot state records: screenshots/before_scenarios.json and screenshots/after_scenarios.json.", "CaptionText"),
              para("Submission location", "Heading2"),
              para("https://github.com/Audatic07/SE_Lab/tree/main/Lab-4"),
              para("The original README is preserved as UPSTREAM_README.md. All changes are in the personal lab repository; no upstream pull request is required.", "CaptionText")]
    build(ROOT / f"{SRN}_Lab4_Report.pdf", story)


def export_chat(session):
    now = datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(timespec="seconds")
    lines = ["# Lab 4 - Actual conversation export", f"SRN: {SRN}", f"Export cutoff: {now} (IST)",
             "", "Visible user request and assistant messages up to the cutoff are reproduced below. "
             "System/developer context, environment metadata, private reasoning, raw tool calls and tool outputs are excluded. "
             "The final delivery message and any subsequent messages occur after this export. "
             "No per-feature student prompts have been invented.", ""]
    for raw in session.read_text().splitlines():
        row = json.loads(raw)
        p = row.get("payload", {})
        if row.get("type") != "response_item" or p.get("type") != "message":
            continue
        if p.get("role") not in {"user", "assistant"}:
            continue
        if p.get("role") == "assistant" and p.get("phase") not in {"commentary", "final"}:
            continue
        content = "\n".join(b.get("text", "") for b in p.get("content", [])
                            if b.get("type") in {"input_text", "output_text"}).strip()
        if not content or content.startswith(("<environment_context>", "<external_codex_apps_open_page>")):
            continue
        label = "Student" if p["role"] == "user" else "Codex"
        lines += [f"## {label}", content, ""]
    (ROOT / "Chat_History.md").write_text("\n".join(lines).rstrip() + "\n")


def chat_pdf():
    story = []
    for block in (ROOT / "Chat_History.md").read_text().split("\n\n"):
        block = block.strip()
        if not block:
            continue
        for line in block.splitlines():
            if line.startswith("# "):
                story.append(para(line[2:], "Title"))
            elif line.startswith("## "):
                story.append(para(line[3:], "Heading2"))
            else:
                story.append(para(line, "ChatText"))
        story.append(Spacer(1, 5))
    build(ROOT / f"{SRN}_Chat_History.pdf", story)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", type=Path)
    args = parser.parse_args()
    if args.session:
        export_chat(args.session)
    report()
    chat_pdf()
    print("Built submission report and chat history PDFs.")
