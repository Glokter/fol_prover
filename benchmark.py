"""
Benchmark harness: runs both provers over all datasets and produces a CSV
plus a human-readable summary.

Usage:
    python benchmark.py                 # run and write results.csv
    python benchmark.py --timeout 10    # custom per-problem timeout
"""

import argparse
import csv
import sys
import time
from pathlib import Path

from datasets import load_all
from baseline import NaiveProver
from improved import FVProver


# Problems in our dataset that are NOT valid in classical FOL.
# They are included to check that both provers handle non-theorems
# by reporting unprovability (or timing out, which is also acceptable
# since FOL is only semi-decidable).
NON_THEOREMS = {"syn_nonthm"}


def run_one(prover, goal, timeout):
    prover.timeout = timeout
    t0 = time.perf_counter()
    result = prover.prove(goal)
    dt = time.perf_counter() - t0
    return result, dt, prover.applications


def verdict(result, expected_theorem):
    """
    Verdict categories:
      'proved'     -- prover said YES, and the goal is a theorem
      'rejected'   -- prover said NO, and the goal is NOT a theorem (correct!)
      'incomplete' -- prover said NO on a theorem (incompleteness, not unsoundness)
      'unsound'    -- prover said YES on a non-theorem (a real bug, should not happen)
      'unknown'    -- timed out / budget exhausted / depth exhausted
    """
    if result is None:
        return "unknown"
    if expected_theorem:
        return "proved" if result else "incomplete"
    else:
        return "rejected" if not result else "unsound"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=10.0,
                    help="per-problem wall-clock timeout in seconds")
    ap.add_argument("--baseline-budget", type=int, default=1_000_000,
                    help="rule-application budget for baseline")
    ap.add_argument("--improved-depth", type=int, default=15,
                    help="maximum quantifier-rule depth for improved")
    ap.add_argument("--out", default="results.csv",
                    help="output CSV path")
    args = ap.parse_args()

    sys.setrecursionlimit(20000)

    # Load all datasets, tagging each problem with its source.
    all_problems = []
    for src, folder in [("pelletier", "datasets/pelletier"),
                        ("syn",       "datasets/syn"),
                        ("generated", "datasets/generated")]:
        for name, goal in load_all(folder):
            all_problems.append((src, name, goal))

    print(f"Loaded {len(all_problems)} problems "
          f"({sum(1 for s,_,_ in all_problems if s=='pelletier')} Pelletier, "
          f"{sum(1 for s,_,_ in all_problems if s=='syn')} SYN, "
          f"{sum(1 for s,_,_ in all_problems if s=='generated')} generated)")
    print(f"Per-problem timeout: {args.timeout}s")
    print()

    header = ("source name  baseline_result baseline_apps baseline_ms  "
              "improved_result improved_apps improved_ms".split())

    rows = []
    print(f"{'source':<10} {'name':<22} "
          f"{'baseline':>20}    {'improved':>20}")
    print("-" * 80)

    for src, name, goal in all_problems:
        expected = name not in NON_THEOREMS

        b = NaiveProver(budget=args.baseline_budget, timeout=args.timeout)
        r_b, t_b, a_b = run_one(b, goal, args.timeout)
        v_b = verdict(r_b, expected)

        i = FVProver(max_qdepth=args.improved_depth, timeout=args.timeout)
        r_i, t_i, a_i = run_one(i, goal, args.timeout)
        v_i = verdict(r_i, expected)

        mk = {"proved": "YES", "rejected": "NO ",
              "unknown": "T/O", "incomplete": "INC", "unsound": "!!!"}
        print(f"{src:<10} {name:<22} "
              f"{mk[v_b]} {a_b:7d} {t_b*1000:8.1f}ms    "
              f"{mk[v_i]} {a_i:7d} {t_i*1000:8.1f}ms")

        rows.append({
            "source": src,
            "name": name,
            "expected": "theorem" if expected else "non-theorem",
            "baseline_verdict": v_b,
            "baseline_apps": a_b,
            "baseline_ms": f"{t_b*1000:.2f}",
            "improved_verdict": v_i,
            "improved_apps": a_i,
            "improved_ms": f"{t_i*1000:.2f}",
        })

    # Write CSV
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for prover_key, label in [("baseline", "Baseline (Algorithm 2)"),
                              ("improved", "Improved (free-var + ID)")]:
        counts = {"proved": 0, "rejected": 0, "unknown": 0,
                  "incomplete": 0, "unsound": 0}
        total_time = 0.0
        for r in rows:
            counts[r[f"{prover_key}_verdict"]] += 1
            total_time += float(r[f"{prover_key}_ms"])
        solved = counts["proved"] + counts["rejected"]
        print(f"\n{label}:")
        print(f"  correctly solved:     {solved:3d}/{len(rows)}")
        print(f"    proved (theorems):  {counts['proved']:3d}")
        print(f"    rejected (non-thm): {counts['rejected']:3d}")
        print(f"  incomplete (theorem reported as non-thm): {counts['incomplete']:3d}")
        print(f"  unknown (timeout/depth): {counts['unknown']:3d}")
        print(f"  unsound (SHOULD BE ZERO): {counts['unsound']:3d}")
        print(f"  total wall-clock time: {total_time/1000:.1f}s")

    print(f"\nDetailed CSV written to {args.out}")


if __name__ == "__main__":
    main()
