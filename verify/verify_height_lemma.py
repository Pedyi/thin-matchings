#!/usr/bin/env python3
"""
verify_height_lemma.py
========================
RECONSTRUCTED SCRIPT -- fresh reimplementation from Lemma [Height] in
thin_matching.tex; not the user's original code (see
verify_parity_lemma.py header for full disclosure).

Checks Lemma [Height]:
  Every chain S_1 subsetneq S_2 subsetneq ... subsetneq S_L in F has L<=n/2.

Method: compute F, build the strict-inclusion DAG, find the longest chain
by dynamic programming (longest path in a DAG), compare to n/2.
"""
import random
from fractions import Fraction as Fr

from lattice import all_pms, build_x, Nplus


def longest_chain(fam):
    fam = sorted(fam, key=len)
    best = {S: 1 for S in fam}
    for i, S in enumerate(fam):
        for T in fam[:i]:
            if T < S and best[T] + 1 > best[S]:
                best[S] = best[T] + 1
    return max(best.values()) if best else 0


if __name__ == "__main__":
    print("=" * 70)
    print("Lemma [Height]: every chain in F has length <= n/2")
    print("=" * 70)
    graphs = [
        (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),
        (12, [(0, 3), (0, 6), (0, 5), (1, 8), (1, 6), (1, 9), (2, 10), (2, 11),
              (2, 8), (3, 7), (3, 9), (4, 10), (4, 7), (4, 11), (5, 8), (5, 6),
              (7, 9), (10, 11)]),
    ]
    rng = random.Random(53)
    max_ratio_seen = Fr(0)
    violations = 0
    instances = 0
    for n, edges in graphs:
        pms = all_pms(n, edges)
        if len(pms) < 2:
            continue
        for trial in range(20):
            k = rng.randint(1, len(pms))
            chosen = rng.sample(pms, k)
            raw = [rng.randint(1, 9) for _ in chosen]
            tot = sum(raw)
            weights = [Fr(r, tot) for r in raw]
            x = build_x(len(edges), chosen, weights)
            fam = Nplus(n, edges, x)
            L = longest_chain(fam)
            instances += 1
            ratio = Fr(L, n)
            if ratio > max_ratio_seen:
                max_ratio_seen = ratio
            if L > n // 2:
                violations += 1
                print(f"  !! VIOLATION n={n} longest chain L={L} > n/2")
    print(f"instances checked      : {instances}")
    print(f"violations             : {violations}")
    print(f"max observed L/n ratio : {max_ratio_seen}  (bound: <=1/2)")
    ok = violations == 0
    print(f">>> Height Lemma intact : {ok}\n")
    print("=" * 70)
    print("PASS" if ok else "FAIL")
    print("=" * 70)
