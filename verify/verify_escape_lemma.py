#!/usr/bin/env python3
"""
verify_escape_lemma.py
========================
RECONSTRUCTED SCRIPT -- fresh reimplementation from Lemma [Escape] in
thin_matching.tex; not the user's original code (see
verify_parity_lemma.py header for full disclosure).

Checks Lemma [Escape]:
  Let P in F and let Y be a nonempty proper subset of P that is even,
  connected (in H), and satisfies 0 < mu(Y) < 1/2. Then either Y in F,
  or some connected component D of H[P \\ Y] satisfies D in F and D ⊊ P.

Works in the support graph H, per the paper's convention.
"""
import itertools
import random
from fractions import Fraction as Fr

from lattice import mu, all_pms, build_x, support, conn, Nplus as family_F


def components_of(H, Z):
    Z = set(Z)
    adj = {v: [] for v in Z}
    for (u, v) in H:
        if u in Z and v in Z:
            adj[u].append(v)
            adj[v].append(u)
    seen = set()
    comps = []
    for v in Z:
        if v in seen:
            continue
        st = [v]
        seen.add(v)
        comp = {v}
        while st:
            a = st.pop()
            for b in adj[a]:
                if b not in seen:
                    seen.add(b)
                    st.append(b)
                    comp.add(b)
        comps.append(frozenset(comp))
    return comps


def check_escape(n, edges, x, max_Y_per_P=200):
    H = support(edges, x)
    fam = family_F(n, edges, x)
    famset = set(fam)
    checked = 0
    violations = 0
    for P in fam:
        Plist = sorted(P)
        candidates = []
        for r in range(2, len(Plist), 2):
            for comb in itertools.combinations(Plist, r):
                Y = frozenset(comb)
                if Y == P or len(Y) == 0:
                    continue
                if not conn(H, Y):
                    continue
                mY = mu(n, edges, x, Y)
                if not (0 < mY < Fr(1, 2)):
                    continue
                candidates.append(Y)
        for Y in candidates[:max_Y_per_P]:
            checked += 1
            if Y in famset:
                continue  # first branch satisfied
            PminusY = P - Y
            comps = components_of(H, PminusY)
            found = any((c in famset and c < P) for c in comps)
            if not found:
                violations += 1
                print(f"  !! ESCAPE VIOLATION P={sorted(P)} Y={sorted(Y)}: "
                      f"neither Y in F, nor any component of H[P\\Y] in F")
    return checked, violations


if __name__ == "__main__":
    print("=" * 70)
    print("Escape Lemma (in the support graph H)")
    print("=" * 70)
    graphs = [
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),
        (12, [(0, 3), (0, 6), (0, 5), (1, 8), (1, 6), (1, 9), (2, 10), (2, 11),
              (2, 8), (3, 7), (3, 9), (4, 10), (4, 7), (4, 11), (5, 8), (5, 6),
              (7, 9), (10, 11)]),
    ]
    rng = random.Random(29)
    total_checked = 0
    total_violations = 0

    # Random small instances often have too small an F to exercise the
    # Escape Lemma's branches at all (0 candidate Y's). The paper's own
    # CE3 instance (12-vertex cubic planar graph, |F|=8) reliably has
    # non-atom members with genuine size->=4 subsets Y of weight in
    # (0,1/2), so include it explicitly.
    from lattice import edge_index
    n12 = 12
    e12 = [(0, 3), (0, 6), (0, 5), (1, 8), (1, 6), (1, 9), (2, 10), (2, 11),
           (2, 8), (3, 7), (3, 9), (4, 10), (4, 7), (4, 11), (5, 8), (5, 6),
           (7, 9), (10, 11)]
    idx12 = edge_index(e12)

    def pm12(*es):
        return [idx12[frozenset(e)] for e in es]

    ce3_x = build_x(len(e12),
                     [pm12((0, 3), (1, 8), (2, 10), (4, 11), (5, 6), (7, 9)),
                      pm12((0, 3), (1, 6), (2, 10), (4, 11), (5, 8), (7, 9)),
                      pm12((0, 3), (1, 6), (2, 11), (4, 10), (5, 8), (7, 9)),
                      pm12((0, 3), (1, 9), (2, 8), (4, 7), (5, 6), (10, 11)),
                      pm12((0, 6), (1, 9), (2, 10), (3, 7), (4, 11), (5, 8))],
                     [Fr(1, 9), Fr(1, 3), Fr(1, 3), Fr(1, 9), Fr(1, 9)])
    c, v = check_escape(n12, e12, ce3_x)
    total_checked += c
    total_violations += v
    print(f"(paper's CE3 instance alone: pairs checked={c}, violations={v})")

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
            c, v = check_escape(n, edges, x)
            total_checked += c
            total_violations += v
    print(f"(P,Y) pairs checked : {total_checked}")
    print(f"violations          : {total_violations}")
    print(f">>> Escape Lemma intact on sweep : {total_violations == 0}\n")
    print("=" * 70)
    print("PASS" if total_violations == 0 else "FAIL")
    print("=" * 70)
