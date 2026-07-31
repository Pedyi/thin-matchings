#!/usr/bin/env python3
"""
verify_increment2_structure.py
================================
RECONSTRUCTED SCRIPT -- fresh reimplementation from Lemma [Increments of
size two] in thin_matching.tex; not the user's original code (see
verify_parity_lemma.py header for full disclosure).

Checks Lemma [Increments of size two]:
  Let P be a parent of S with S\\P = {u,v}. Then uv is an edge of H (so
  H[{u,v}] is connected), and mu({u,v}) < 1.

Random small graphs rarely happen to produce a unique-parent, size-2
increment, so we also explicitly re-check the paper's own CE1 witness
(Proposition ce1, the Q3 instance) where this configuration is guaranteed
to occur: S={1,3,5,7}, parent P={1,5}, increment {3,7}.
"""
import itertools
import random
from fractions import Fraction as Fr

from lattice import mu, all_pms, build_x, support, conn, Nplus, parents, edge_index


def check_instance(n, edges, x):
    H = support(edges, x)
    fam = Nplus(n, edges, x)
    checked = 0
    violations = 0
    for S in fam:
        par = parents(S, fam)
        if len(par) != 1:
            continue
        P = par[0]
        inc = S - P
        if len(inc) != 2:
            continue
        checked += 1
        u, v = tuple(inc)
        is_edge = frozenset((u, v)) in {frozenset(e) for e in H}
        m_uv = mu(n, edges, x, inc)
        ok = is_edge and (m_uv < 1)
        if not ok:
            violations += 1
            print(f"  !! VIOLATION S={sorted(S)} P={sorted(P)} inc={u,v} "
                  f"is_edge={is_edge} mu={m_uv}")
    return checked, violations


if __name__ == "__main__":
    print("=" * 70)
    print("Lemma [Increments of size two]")
    print("=" * 70)

    # explicit CE1 witness from Proposition ce1 (guaranteed to trigger)
    n = 8
    edges = [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]
    idx = edge_index(edges)

    def pm(*es):
        return [idx[frozenset(e)] for e in es]

    ce1_x = build_x(len(edges),
                     [pm((0, 4), (1, 5), (2, 6), (3, 7)),
                      pm((0, 4), (6, 7), (1, 5), (2, 3)),
                      pm((0, 4), (5, 7), (1, 3), (2, 6)),
                      pm((4, 6), (0, 2), (1, 5), (3, 7))],
                     [Fr(1, 3), Fr(1, 6), Fr(1, 6), Fr(1, 3)])
    c, v = check_instance(n, edges, ce1_x)
    print(f"(paper's CE1 instance: increment-2 members found={c}, "
          f"violations={v})")

    total_checked, total_viol = c, v
    rng = random.Random(67)
    graphs = [
        (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        (12, [(0, 3), (0, 6), (0, 5), (1, 8), (1, 6), (1, 9), (2, 10), (2, 11),
              (2, 8), (3, 7), (3, 9), (4, 10), (4, 7), (4, 11), (5, 8), (5, 6),
              (7, 9), (10, 11)]),
    ]
    for gn, ge in graphs:
        pms = all_pms(gn, ge)
        if len(pms) < 2:
            continue
        for trial in range(25):
            k = rng.randint(1, len(pms))
            chosen = rng.sample(pms, k)
            raw = [rng.randint(1, 9) for _ in chosen]
            tot = sum(raw)
            weights = [Fr(r, tot) for r in raw]
            x = build_x(len(ge), chosen, weights)
            c2, v2 = check_instance(gn, ge, x)
            total_checked += c2
            total_viol += v2
    print(f"total increment-2 members examined : {total_checked}")
    print(f"total violations                   : {total_viol}")
    ok = total_viol == 0
    print(f">>> Lemma intact : {ok}\n")
    print("=" * 70)
    print("PASS" if ok else "FAIL")
    print("=" * 70)
