#!/usr/bin/env python3
"""Pre-demo check CLI

Runs `demo_check.py` and the deterministic `truth_classifier` on a small
set of sample inputs. Exits non-zero if demo is UNSAFE or any classifier
unit assertions fail.
"""
import subprocess
import sys
import json
from truth_classifier import classify


def run_demo_check(backend_url="http://localhost:8000"):
    # Run demo_check.py as subprocess
    cmd = [sys.executable, "demo_check.py", "--backend-url", backend_url]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = proc.stdout.strip()
    status = "UNSAFE"
    if out == "SAFE":
        status = "SAFE"
    print(f"demo_check: {status}")
    return status == "SAFE"


def run_classifier_smoke():
    samples = [
        {"headline": "This is a hoax"},
        {"headline": "Official from reliable.org", "source": "reliable.org"},
    ]
    ok = True
    for s in samples:
        r = classify(s)
        if not isinstance(r.get("truth_level"), int):
            ok = False
    print(f"classifier_smoke: {'OK' if ok else 'FAIL'}")
    return ok


def main():
    backend = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    demo_ok = run_demo_check(backend)
    cls_ok = run_classifier_smoke()
    if demo_ok and cls_ok:
        print("PRE-DEMO CHECKS PASSED")
        sys.exit(0)
    else:
        print("PRE-DEMO CHECKS FAILED")
        sys.exit(2)


if __name__ == "__main__":
    main()
