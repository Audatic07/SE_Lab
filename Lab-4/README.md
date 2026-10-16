# Lab 4 - Missile Command

**SRN:** PES2UG24CS036

**Date:** 16 October 2026

**Assigned repository:** https://github.com/SETAPESU26/33_missileCommand

**Baseline commit:** `b4318a97def23a2fe945a9a78f713c83ebf6990f`

**Submission:** https://github.com/Audatic07/SE_Lab/tree/main/Lab-4

## Deliverables

- [Updated Python game](game.py) and [pinned dependency](requirements.txt).
- [Submission report](PES2UG24CS036_Lab4_Report.pdf) with task explanations and screenshot evidence.
- [Chat history PDF](PES2UG24CS036_Chat_History.pdf) and [text export](Chat_History.md).
- [Before/after screenshots](screenshots/) and reproducible scenario descriptions.
- [Regression tests](tests/test_game.py) and [verification results](verification.txt).
- [Original assignment README](UPSTREAM_README.md), preserved unchanged.

Screenshots replace both videos at the student's explicit request. No videos are included.

## Run

Python 3.10 or later is required. From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python game.py
```

Click above the ground to fire. Press **R** to reset. Close the window to quit.
The game automatically chooses the closest living battery with ammunition.

## Completed tasks

| Task | Change | Evidence |
| --- | --- | --- |
| 1. Battery selection | Filter out empty/destroyed batteries; return `None` safely if all are unavailable. | `before_02_battery_fallback.png`, `after_02_battery_fallback.png` |
| 2. Explosion colors | Interpolate white -> yellow -> orange -> dark red; clamp lifetime progress. | `after_03_explosion_colors.png` |
| 3. City destruction | Show a three-second warning, with a critical message when two or fewer cities remain. | `after_04_city_warning.png` |
| 4. City repair | Rebuild one destroyed city for each newly crossed 2,000-point milestone; show the next milestone and rebuild notice. | `after_05_before_repair.png`, `after_06_city_repaired.png` |

Repairs are consumed at each milestone even if all cities are healthy; they are not banked.
Crossing multiple milestones in one score increase awards each milestone once.
Destroyed batteries are restored at the next wave, as in the original game.

Additional fixes needed for expected gameplay: interceptors snap exactly to their targets,
waves wait for flying interceptors, expired explosions cannot cause phantom collisions,
and a missile on the blast boundary counts as intercepted.

## Verify

```bash
python -m unittest discover -s tests -v
python tools/capture_screenshots.py --phase after
```

The tests and screenshot generator use SDL's dummy video/audio drivers, so they also run
on a machine without a graphical display. `python game.py` opens the normal game window.
All 26 regression tests passed on Python 3.13.15 and Pygame 2.6.1. The event-loop test
checks mouse, R, and quit event dispatch; the remaining tests exercise game behavior.

## Screenshot provenance

All PNGs are unedited 800 x 600 captures of the actual Pygame display surface. They are
scripted, seeded scenarios, not a claim of an uninterrupted manual play session.
The generator uses real launch, update, collision, impact and draw methods. It stages
missile positions, explosion ages, and a score of 1,975 to make particular features visible.
The repair then earns the final 25 points through a real missile/explosion collision.
The scenario JSON files record ammo, score, interceptor count and city count.

The baseline was cloned and executed before `game.py` was edited. To reproduce it:

```bash
git clone https://github.com/SETAPESU26/33_missileCommand.git /tmp/missile-command-original
git -C /tmp/missile-command-original checkout b4318a97def23a2fe945a9a78f713c83ebf6990f
python tools/capture_screenshots.py --source /tmp/missile-command-original/game.py --phase before
```

## AI assistance record

This work was completed in one Codex conversation using the student's actual request,
followed by code inspection, implementation, regression checks, and visual review.
The chat export preserves the actual user request and assistant messages through its
stated export cutoff. It does not invent separate student prompts for each feature.
System/developer messages, private reasoning, credentials, and raw tool calls are excluded.
The code, test suite, scenario generator, and verification results provide the technical record.

The source was cloned into a temporary checkout and copied here, so `Lab-4` is a normal
folder in the personal lab repository, not a nested Git repository or submodule.
No pull request was opened against the assigned repository.
