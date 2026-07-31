#!/usr/bin/env python3
"""
measure_Nplus.py
==================
RECONSTRUCTED SCRIPT -- fresh reimplementation of the measurement script
referenced throughout thin_matching.tex and its README (Definition N+,
Open Problem [Main]: is N+ = O(n)?); not the user's original code (see
verify_parity_lemma.py header for full disclosure).

Sweeps a library of small instances -- random graphs, the Theta_t
extremal family (Haqi-Oveis Gharan Lemma 1.2, see generators/gen_gadget.py
for provenance), and random asymmetric points x in PM(G) -- and reports
N+ = |F| against n, tracking the max observed ratio N+/n.

This is EVIDENCE for the open conjecture N+ = O(n), not a proof; a bounded
ratio on a finite sweep never establishes an asymptotic bound. See Open
Problem [Main] in thin_matching.tex, Section "Open problems".
"""
import itertools
import os
import random
import sys
from fractions import Fraction as Fr

from lattice import all_pms, build_x, Nplus

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generators"))


def sweep_random_graphs(rows, rng, trials_per_graph=15):
    graphs = [
        (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),
        (10, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (5, 6), (6, 7), (7, 8),
              (8, 9), (9, 5), (0, 5), (1, 6), (2, 7), (3, 8), (4, 9)]),
        (12, [(0, 3), (0, 6), (0, 5), (1, 8), (1, 6), (1, 9), (2, 10), (2, 11),
              (2, 8), (3, 7), (3, 9), (4, 10), (4, 7), (4, 11), (5, 8), (5, 6),
              (7, 9), (10, 11)]),
    ]
    for n, edges in graphs:
        pms = all_pms(n, edges)
        if len(pms) < 2:
            continue
        for _ in range(trials_per_graph):
            k = rng.randint(1, len(pms))
            chosen = rng.sample(pms, k)
            raw = [rng.randint(1, 9) for _ in chosen]
            tot = sum(raw)
            weights = [Fr(r, tot) for r in raw]
            x = build_x(len(edges), chosen, weights)
            fam = Nplus(n, edges, x)
            rows.append((n, len(fam), "random"))


def sweep_theta_t(rows):
    try:
        from gen_gadget import theta_t
    except ImportError:
        print("  (gen_gadget not importable; skipping Theta_t sweep)")
        return
    for t in range(2, 6):
        n, edges, x = theta_t(t)
        fam = Nplus(n, edges, x)
        rows.append((n, len(fam), f"theta_{t}"))


if __name__ == "__main__":
    print("=" * 70)
    print("Measuring N+ vs n  (evidence for Open Problem [Main]: N+ = O(n)?)")
    print("=" * 70)
    rng = random.Random(97)
    rows = []
    sweep_random_graphs(rows, rng)
    sweep_theta_t(rows)

    print(f"{'source':>10} {'n':>4} {'N+':>5} {'N+/n':>8}")
    max_ratio = Fr(0)
    max_ratio_source = None
    for n, Np, source in rows:
        ratio = Fr(Np, n)
        if ratio > max_ratio:
            max_ratio = ratio
            max_ratio_source = (source, n, Np)
        print(f"{source:>10} {n:>4} {Np:>5} {str(ratio):>8}")

    print(f"\nmax N+/n observed : {max_ratio}"
          f"{f'  (source={max_ratio_source[0]}, n={max_ratio_source[1]}, N+={max_ratio_source[2]})' if max_ratio_source else ''}")
    print("This is a finite sweep on small n; it is evidence, not a proof, "
          "for the conjecture N+ = O(n) (Open Problem [Main]). The paper "
          "itself flags that all its evidence is confined to graphs with "
          "at most 18 vertices where the poset F never exceeded height 3, "
          "and that the regime of tall posets is untested.")
