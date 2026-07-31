#!/usr/bin/env python3
"""
verify_Nplus_reduction.py
==========================
RECONSTRUCTED SCRIPT -- fresh reimplementation from Section "Reduction to a
counting problem" of thin_matching.tex; not the user's original code
(see verify_parity_lemma.py header for full disclosure).

Checks Theorem [N+ <= n  =>  thin(G,x) <= n]:
  N+ = #{ S primitive : 0 < x(delta(S)) < 1/2 }.
  If N+ <= n then thin(G,x) <= n.

This is proved in the paper via Phi(n) < 1 (Theorem [Certificate] at
alpha=n). Here we check the CONCLUSION directly and exactly: whenever the
count N+ computed on a random instance is <= n, brute-force thin(G,x) and
confirm it is <= n.
"""
import itertools
from fractions import Fraction as Fr
import random

from lattice import mu, all_pms, build_x, Nplus


def Nplus_count(n, edges, x):
    return len(Nplus(n, edges, x))


def exact_thin(n, edges, x):
    Hidx = [i for i, w in enumerate(x) if w > 0]
    Hedges = [edges[i] for i in Hidx]
    pms = all_pms(n, Hedges)
    if not pms:
        return None
    all_cuts = []
    for r in range(1, n):
        for comb in itertools.combinations(range(n), r):
            S = frozenset(comb)
            mS = mu(n, edges, x, S)
            if mS > 0:
                all_cuts.append((S, mS))
    best = None
    for pm_local in pms:
        M_global = [Hidx[i] for i in pm_local]
        worst = Fr(0)
        for S, mS in all_cuts:
            cross = sum(1 for i in M_global
                        if (edges[i][0] in S) != (edges[i][1] in S))
            ratio = Fr(cross) / mS
            if ratio > worst:
                worst = ratio
        if best is None or worst < best:
            best = worst
    return best


if __name__ == "__main__":
    print("=" * 70)
    print("Theorem: N+ <= n  =>  thin(G,x) <= n")
    print("=" * 70)
    graphs = [
        (4, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]),
        (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),
    ]
    rng = random.Random(19)
    checked = 0
    violations = 0
    np_le_n_cases = 0
    for n, edges in graphs:
        pms = all_pms(n, edges)
        if len(pms) < 2:
            continue
        for trial in range(10):
            k = rng.randint(1, len(pms))
            chosen = rng.sample(pms, k)
            raw = [rng.randint(1, 9) for _ in chosen]
            tot = sum(raw)
            weights = [Fr(r, tot) for r in raw]
            x = build_x(len(edges), chosen, weights)
            npc = Nplus_count(n, edges, x)
            checked += 1
            if npc <= n:
                np_le_n_cases += 1
                th = exact_thin(n, edges, x)
                if th is not None and th > n:
                    violations += 1
                    print(f"  !! VIOLATION n={n} N+={npc} thin={th}")
    print(f"instances checked          : {checked}")
    print(f"instances with N+ <= n     : {np_le_n_cases}")
    print(f"violations of thin<=n      : {violations}")
    print(f">>> Theorem intact on sweep : {violations == 0}\n")
    print("=" * 70)
    print("PASS" if violations == 0 else "FAIL")
    print("=" * 70)
