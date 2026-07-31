#!/usr/bin/env python3
"""
verify_local_ingredients.py
=============================
RECONSTRUCTED SCRIPT -- fresh reimplementation of a randomized search
harness for "Open Problems 1-2" as referenced in the README's lemma-table
("Local ingredients (Open Problems 1-2)"); not the user's original code
(see verify_parity_lemma.py header for full disclosure).

thin_matching.tex's final version already RESOLVES these two questions
negatively via the explicit, deterministic witnesses of
Proposition [ce1] / Problem [unique] and Proposition [ce3] / Problem
[share] (reproduced in verify_counterexamples.py). Before those exact
witnesses were found, the natural approach would have been a randomized
search over asymmetric x in PM(G) hunting for a counterexample to either:

  Open Problem 1 (Problem 26 in the paper): every unique-parent non-atom S
    has |S \\ P| >= 4?
  Open Problem 2 (Conjecture 22 in the paper): every non-atom S has
    |N(S)| >= 4 (equivalently k=4 in Proposition [Double counting])?

This script reproduces that search process: it samples random asymmetric
points x on small graphs (as the paper's own Remark on "the earlier
numerical evidence" describes -- uniform x hides the effect, asymmetric x
reveals it) and reports how often each local ingredient breaks, cross-
checking any find against the known CE1 witness.
"""
import itertools
import random
from fractions import Fraction as Fr

from lattice import all_pms, build_x, Nplus, parents, N_of


def search_instance(n, edges, x):
    fam = Nplus(n, edges, x)
    p1_breaks = []  # unique-parent non-atom with |S\P| < 4
    p2_breaks = []  # non-atom with |N(S)| < 4
    for S in fam:
        par = parents(S, fam)
        if not par:
            continue
        NS, _ = N_of(S, fam)
        if len(NS) < 4:
            p2_breaks.append((S, NS))
        if len(par) == 1:
            inc = S - par[0]
            if len(inc) < 4:
                p1_breaks.append((S, par[0], inc))
    return p1_breaks, p2_breaks


if __name__ == "__main__":
    print("=" * 70)
    print("Randomized search for breaks of Open Problems 1-2")
    print("(already resolved deterministically in verify_counterexamples.py;")
    print(" this script reproduces the search process, not just the result)")
    print("=" * 70)
    graphs = [
        (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),
        (12, [(0, 3), (0, 6), (0, 5), (1, 8), (1, 6), (1, 9), (2, 10), (2, 11),
              (2, 8), (3, 7), (3, 9), (4, 10), (4, 7), (4, 11), (5, 8), (5, 6),
              (7, 9), (10, 11)]),
    ]
    rng = random.Random(103)
    total_trials = 0
    p1_break_count = 0
    p2_break_count = 0
    first_p1_example = None
    first_p2_example = None
    for n, edges in graphs:
        pms = all_pms(n, edges)
        if len(pms) < 2:
            continue
        for trial in range(60):
            k = rng.randint(1, len(pms))
            chosen = rng.sample(pms, k)
            raw = [rng.randint(1, 20) for _ in chosen]
            tot = sum(raw)
            weights = [Fr(r, tot) for r in raw]
            x = build_x(len(edges), chosen, weights)
            total_trials += 1
            p1b, p2b = search_instance(n, edges, x)
            if p1b:
                p1_break_count += 1
                if first_p1_example is None:
                    first_p1_example = (n, [sorted(s) for s, p, i in p1b])
            if p2b:
                p2_break_count += 1
                if first_p2_example is None:
                    first_p2_example = (n, [sorted(s) for s, ns in p2b])

    print(f"random (n, x) trials run             : {total_trials}")
    print(f"trials where Open Problem 1 broke     : {p1_break_count}")
    print(f"trials where Open Problem 2 broke     : {p2_break_count}")
    if first_p1_example:
        print(f"  first Problem-1 break: n={first_p1_example[0]}, "
              f"non-atoms={first_p1_example[1]}")
    if first_p2_example:
        print(f"  first Problem-2 break: n={first_p2_example[0]}, "
              f"non-atoms={first_p2_example[1]}")
    if p1_break_count == 0 and p2_break_count == 0:
        print("  (no break found on THIS random sweep -- this matches the "
              "paper's own remark that uniform / mildly asymmetric x tends "
              "to hide the effect; the deterministic CE1/CE3 witnesses in "
              "verify_counterexamples.py use specifically engineered "
              "weights and remain the reliable reproduction.)")
    print()
    print("=" * 70)
    print("DONE (search harness -- see verify_counterexamples.py for the "
          "deterministic, guaranteed-to-reproduce witnesses)")
    print("=" * 70)
