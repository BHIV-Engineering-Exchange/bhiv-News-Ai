#!/usr/bin/env python3
"""Determinism test harness for `truth_classifier.classify`.

Runs multiple classification iterations on the same inputs to ensure
deterministic outputs and generates a short validation report.
"""
import json
import os
from truth_classifier import classify
from datetime import datetime

SAMPLES = [
    {"id": 1, "headline": "This is a hoax story", "text": "Completely fabricated", "source": "unknown"},
    {"id": 2, "headline": "Official release from reliable.org", "source": "reliable.org", "confidence": 0.95},
    {"id": 3, "headline": "Local report reportedly says...", "text": "alleged theft reported"},
    {"id": 4, "headline": "Community meeting announced", "text": "Town hall at 6pm"},
    {"id": 5, "headline": "Satire: politicians eat bananas", "text": "This is parody"},
]

ITERATIONS = 100


def run():
    results = {"checked_at": datetime.now().isoformat(), "iterations": ITERATIONS, "samples": []}
    stable = True

    for s in SAMPLES:
        outs = []
        for i in range(ITERATIONS):
            o = classify(s)
            outs.append(o)

        # Compare all outputs to the first
        first = outs[0]
        inconsistent = [o for o in outs if o != first]

        sample_report = {"id": s["id"], "input": s, "first_output": first, "inconsistent_count": len(inconsistent)}
        results["samples"].append(sample_report)
        if inconsistent:
            stable = False

    results["stable"] = stable

    # Write report files
    base = os.path.dirname(__file__)
    json_path = os.path.join(base, "determinism_validation_report.json")
    md_path = os.path.join(base, "determinism_validation_report.md")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Determinism Validation Report\n\nChecked at: {results['checked_at']}\n\n")
        f.write(f"Iterations per sample: {results['iterations']}\n\n")
        f.write(f"Overall stable: {results['stable']}\n\n")
        for s in results["samples"]:
            f.write(f"- Sample {s['id']}: inconsistent_count = {s['inconsistent_count']} -> first_output = {s['first_output']}\n")

    print(f"Wrote: {json_path} and {md_path}")


if __name__ == "__main__":
    run()
