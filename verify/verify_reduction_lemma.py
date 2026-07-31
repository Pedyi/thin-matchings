#!/usr/bin/env python3
"""
verify_reduction_lemma.py
==========================
RECONSTRUCTED SCRIPT (see verify_parity_lemma.py header for the disclosure
that this is a fresh reimplementation from the paper, not recovered code).

Checks Lemma [Reduction] (Section "Primitive cuts and the Reduction Lemma"):
  Let beta >= n/2 and let M subseteq supp(x) be a perfect matching such that
  |M ∩ delta(S)| <= beta * x(delta(S)) for every PRIMITIVE cut S with
  x(delta(S)) > 0. Then M is beta-thin, i.e. the same bound holds for
  EVERY cut S subseteq V (not just primitive ones).

Method: for small random graphs and random x in PM(G), pick a random PM
M subseteq supp(x), set beta = n/2 (the tightest allowed value), check
whether M satisfies the hypothesis on all primitive cuts; if it does,
verify the conclusion by brute-force over ALL 2^n cuts.
"""
import itertools
import random
from fractions import Fraction as Fr

from lattice import mu, all_pms, build_x, support, conn, edge_index


def is_primitive(n, H, S):
    S = set(S)
    if len(S) % 2 != 0 or len(S) == 0 or len(S) == n:
        return False
    return conn(H, S) and conn(H, set(range(n)) - S)


def check_instance(n, edges, x, M_edges, beta, rng):
    H = support(edges, x)
    # hypothesis: bound on primitive cuts only
    hyp_ok = True
    for r in range(2, n, 2):
        for comb in itertools.combinations(range(n), r):
            S = frozenset(comb)
            if not is_primitive(n, H, S):
                continue
            mS = mu(n, edges, x, S)
            if mS <= 0:
                continue
            cross = sum(1 for i in M_edges
                        if (edges[i][0] in S) != (edges[i][1] in S))
            if cross > beta * mS:
                hyp_ok = False
    if not hyp_ok:
        return None  # hypothesis not satisfied on this random M; skip

    # conclusion: bound must hold on ALL cuts
    worst_ratio = Fr(0)
    conclusion_ok = True
    for r in range(0, n + 1):
        for comb in itertools.combinations(range(n), r):
            S = frozenset(comb)
            mS = mu(n, edges, x, S)
            if mS <= 0:
                continue
            cross = sum(1 for i in M_edges
                        if (edges[i][0] in S) != (edges[i][1] in S))
            ratio = Fr(cross) / mS
            if ratio > worst_ratio:
                worst_ratio = ratio
            if cross > beta * mS:
                conclusion_ok = False
    return conclusion_ok, worst_ratio


if __name__ == "__main__":
    print("=" * 70)
    print("Reduction Lemma -- beta >= n/2, primitive-cut bound => all-cut bound")
    print("=" * 70)
    rng = random.Random(11)
    graphs = [
        (4, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]),
        (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),
    ]
    checked = 0
    failures = 0
    for n, edges in graphs:
        pms = all_pms(n, edges)
        if len(pms) < 2:
            continue
        beta = Fr(n, 2)
        for trial in range(30):
            k = rng.randint(1, len(pms))
            chosen = rng.sample(pms, k)
            raw = [rng.randint(1, 9) for _ in chosen]
            tot = sum(raw)
            weights = [Fr(r, tot) for r in raw]
            x = build_x(len(edges), chosen, weights)
            M_edges = rng.choice(pms)
            # M must actually lie in supp(x)
            H_idx = {i for i, w in enumerate(x) if w > 0}
            if not set(M_edges).issubset(H_idx):
                continue
            result = check_instance(n, edges, x, M_edges, beta, rng)
            if result is None:
                continue
            checked += 1
            ok, worst = result
            if not ok:
                failures += 1
                print(f"  !! FAILURE on n={n}, beta={beta}, worst ratio={worst}")
    print(f"instances where hypothesis held and were checked : {checked}")
    print(f"conclusion failures                               : {failures}")
    print(f">>> Reduction Lemma intact on sweep : {failures == 0}\n")
    print("=" * 70)
    print("PASS" if failures == 0 else "FAIL")
    print("=" * 70)
