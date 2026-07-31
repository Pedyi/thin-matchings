#!/usr/bin/env python3
"""
verify_trichotomy_and_component.py
====================================
RECONSTRUCTED SCRIPT -- fresh reimplementation from Section "Structure of
the critical family" of thin_matching.tex; not the user's original code
(see verify_parity_lemma.py header for full disclosure).

Checks two results:

Lemma [Components]: If x(delta(Z)) < 1 then every connected component of
G[Z] (i.e. H[Z], per the support convention) has even cardinality and cut
weight at most x(delta(Z)).

Lemma [Trichotomy]: If P, Q are in F = {primitive S : 0 < mu(S) < 1/2} and
P, Q cross (all of P∩Q, P\\Q, Q\\P nonempty), then at least one of these
three pieces has cut weight in (0, 1/2).
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


def check_components(n, edges, x, rng, samples=40):
    H = support(edges, x)
    checked = 0
    violations = 0
    all_subsets = [frozenset(c) for r in range(1, n)
                   for c in itertools.combinations(range(n), r)]
    rng.shuffle(all_subsets)
    for Z in all_subsets[:samples]:
        mZ = mu(n, edges, x, Z)
        if mZ >= 1:
            continue
        checked += 1
        for comp in components_of(H, Z):
            ok_parity = len(comp) % 2 == 0
            mcomp = mu(n, edges, x, comp)
            ok_weight = mcomp <= mZ
            if not (ok_parity and ok_weight):
                violations += 1
                print(f"  !! COMPONENT VIOLATION Z={sorted(Z)} "
                      f"comp={sorted(comp)} parity_ok={ok_parity} "
                      f"weight_ok={ok_weight} (mu(comp)={mcomp}, mu(Z)={mZ})")
    return checked, violations


def check_trichotomy(n, edges, x):
    fam = family_F(n, edges, x)
    checked = 0
    violations = 0
    for P, Q in itertools.combinations(fam, 2):
        inter, pminusq, qminusp = P & Q, P - Q, Q - P
        if not (inter and pminusq and qminusp):
            continue  # not crossing
        checked += 1
        weights = [mu(n, edges, x, inter), mu(n, edges, x, pminusq),
                   mu(n, edges, x, qminusp)]
        if not any(0 < w < Fr(1, 2) for w in weights):
            violations += 1
            print(f"  !! TRICHOTOMY VIOLATION P={sorted(P)} Q={sorted(Q)} "
                  f"weights={weights}")
    return checked, violations


if __name__ == "__main__":
    print("=" * 70)
    print("Component Lemma + Trichotomy Lemma")
    print("=" * 70)
    graphs = [
        (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),
        (12, [(0, 3), (0, 6), (0, 5), (1, 8), (1, 6), (1, 9), (2, 10), (2, 11),
              (2, 8), (3, 7), (3, 9), (4, 10), (4, 7), (4, 11), (5, 8), (5, 6),
              (7, 9), (10, 11)]),
    ]
    rng = random.Random(23)
    comp_checked = comp_viol = tri_checked = tri_viol = 0

    # The paper's own CE3 instance (12-vertex cubic planar graph) is known
    # to produce a large, non-laminar F (37 crossing pairs), so we include
    # its exact x explicitly to make sure Trichotomy is actually exercised,
    # not just vacuously "0 crossing pairs found" on easy random instances.
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
    c, v = check_components(n12, e12, ce3_x, rng, samples=60)
    comp_checked += c
    comp_viol += v
    c2, v2 = check_trichotomy(n12, e12, ce3_x)
    tri_checked += c2
    tri_viol += v2
    print(f"(paper's CE3 instance: |F|={len(family_F(n12, e12, ce3_x))}, "
          f"crossing pairs tested={c2})")

    for n, edges in graphs:
        pms = all_pms(n, edges)
        if len(pms) < 2:
            continue
        for trial in range(6):
            k = rng.randint(1, len(pms))
            chosen = rng.sample(pms, k)
            raw = [rng.randint(1, 9) for _ in chosen]
            tot = sum(raw)
            weights = [Fr(r, tot) for r in raw]
            x = build_x(len(edges), chosen, weights)
            c, v = check_components(n, edges, x, rng)
            comp_checked += c
            comp_viol += v
            c2, v2 = check_trichotomy(n, edges, x)
            tri_checked += c2
            tri_viol += v2
    print(f"Component Lemma: subsets checked={comp_checked}, "
          f"violations={comp_viol}")
    print(f"Trichotomy Lemma: crossing pairs checked={tri_checked}, "
          f"violations={tri_viol}\n")
    ok = (comp_viol == 0 and tri_viol == 0)
    print("=" * 70)
    print("PASS" if ok else "FAIL")
    print("=" * 70)
