#!/usr/bin/env python3
"""
verify_phi_certificate.py
==========================
RECONSTRUCTED SCRIPT -- fresh reimplementation from Section "The
Phi-certificate" of thin_matching.tex; not the user's original code
(see verify_parity_lemma.py header for full disclosure).

Checks Theorem [Certificate]:
  If alpha >= n/2 and Phi(alpha) < 1, then thin(G,x) <= alpha,
  where for a primitive cut S, mu_S = x(delta(S)),
    k(alpha,mu) = least EVEN integer strictly greater than alpha*mu,
    Phi(alpha)  = sum over primitive S with mu_S>0 of mu_S / k(alpha,mu_S)
                  (term is 0 if k(alpha,mu_S) > n/2).

Method: brute-force compute thin(G,x) = min over PM M subseteq supp(x) of
max over cuts S with mu_S>0 of |M ∩ delta(S)| / mu_S, exactly in exact
rational arithmetic, and compare against alpha whenever Phi(alpha) < 1.
"""
import itertools
from fractions import Fraction as Fr

from lattice import mu, all_pms, build_x, support, primitive_cuts_one_sided


def k_even(alpha, m):
    """Least even integer strictly greater than alpha*m."""
    val = alpha * m
    # smallest even integer > val
    k = 2 * (int(val // 2) + 1)
    while k <= val:
        k += 2
    return k


def phi(alpha, n, edges, x):
    # each unordered primitive cut counted exactly once (side avoiding vtx 0)
    total = Fr(0)
    for S in primitive_cuts_one_sided(n, edges, x, weight_min=Fr(0)):
        mS = mu(n, edges, x, S)
        k = k_even(alpha, mS)
        if k > Fr(n, 2):
            continue
        total += mS / k
    return total


def exact_thin(n, edges, x):
    """thin(G,x) = min over PM subset of supp(x) of max ratio over all cuts."""
    Hidx = [i for i, w in enumerate(x) if w > 0]
    Hedges = [edges[i] for i in Hidx]
    pms = all_pms(n, Hedges)
    if not pms:
        return None
    best = None
    all_cuts = []
    for r in range(1, n):
        for comb in itertools.combinations(range(n), r):
            S = frozenset(comb)
            mS = mu(n, edges, x, S)
            if mS > 0:
                all_cuts.append((S, mS))
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
    print("Phi-certificate -- Phi(alpha) < 1  =>  thin(G,x) <= alpha")
    print("=" * 70)
    graphs = [
        (4, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]),
        (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),  # Q3
    ]
    import random
    rng = random.Random(3)
    checked = 0
    violations = 0
    for n, edges in graphs:
        pms = all_pms(n, edges)
        if len(pms) < 2:
            continue
        for trial in range(8):
            k = rng.randint(1, len(pms))
            chosen = rng.sample(pms, k)
            raw = [rng.randint(1, 9) for _ in chosen]
            tot = sum(raw)
            weights = [Fr(r, tot) for r in raw]
            x = build_x(len(edges), chosen, weights)
            th = exact_thin(n, edges, x)
            if th is None:
                continue
            for alpha in [Fr(n, 2), Fr(n, 2) + 1, Fr(3 * n, 4), Fr(n)]:
                if alpha < Fr(n, 2):
                    continue
                p = phi(alpha, n, edges, x)
                checked += 1
                if p < 1:
                    ok = th <= alpha
                    if not ok:
                        violations += 1
                        print(f"  !! VIOLATION n={n} alpha={alpha} "
                              f"Phi={p} thin={th}")
    print(f"(alpha, x) pairs checked : {checked}")
    print(f"violations               : {violations}")
    print(f">>> Certificate intact on sweep : {violations == 0}\n")
    print("=" * 70)
    print("PASS" if violations == 0 else "FAIL")
    print("=" * 70)
