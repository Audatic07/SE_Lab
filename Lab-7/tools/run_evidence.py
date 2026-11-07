"""Run real subprocesses and retain their unedited stdout/stderr plus metadata."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(name, command, cwd, stdin=None, expected=0):
    result = subprocess.run(command, cwd=cwd, input=stdin, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=120)
    record = {"command": command, "cwd": str(cwd), "stdin": stdin,
              "exit_code": result.returncode, "expected_exit_code": expected,
              "timestamp_utc": datetime.now(timezone.utc).isoformat()}
    target = ROOT / "evidence" / "logs" / name
    target.with_suffix(".txt").write_text(result.stdout)
    target.with_suffix(".json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"{name}: exit {result.returncode} (expected {expected})")
    print(result.stdout)
    if result.returncode != expected:
        raise SystemExit(f"Unexpected exit code for {name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("before", "after"))
    args = parser.parse_args()
    if args.phase == "before":
        # The frozen discovery suite is kept with the unmodified application.
        run("01_before_normal", [sys.executable, "spam_scoring.py"], ROOT / "original",
            "offers@Deals.com\nVisit https://example.com/deal now\nFREE prize NOW\n")
        run("02_before_invalid", [sys.executable, "spam_scoring.py"], ROOT / "original",
            "\n\n\n", expected=1)
        run("03_before_fuzz", [sys.executable, "-m", "pytest", "test_discovery.py", "-q",
                              "-k", "not text_no_crash", "--tb=short", "--color=no"], ROOT / "original", expected=1)
        run("03b_before_text_fuzz", [sys.executable, "-m", "pytest", "test_discovery.py", "-q",
                                   "-k", "text_no_crash", "--tb=short", "--color=no"], ROOT / "original", expected=1)
    else:
        run("04_after_normal", [sys.executable, "spam_scoring.py"], ROOT,
            "offers@Deals.com\nVisit https://example.com/deal now\nFREE prize NOW\n")
        run("05_after_invalid", [sys.executable, "spam_scoring.py"], ROOT, "\n\n\n")
        run("06_after_discovery", [sys.executable, "-m", "pytest", "test_spam_scoring.py",
                                   "-k", "no_crash", "-q", "--tb=short", "--color=no"], ROOT)
        run("07_after_full_suite", [sys.executable, "-m", "pytest", "test_spam_scoring.py",
                                   "-v", "--tb=short", "--color=no",
                                   "--hypothesis-show-statistics"], ROOT)
