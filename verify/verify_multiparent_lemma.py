#!/usr/bin/env python3
"""
verify_multiparent_lemma.py
=============================
RECONSTRUCTED SCRIPT -- fresh reimplementation from Lemma [Several parents]
in thin_matching.tex; not the user's original code (see
verify_parity_lemma.py header for full disclosure).

Checks Lemma [Several parents]:
  If |Par(S)| >= 2 (S has at least two parents in F) then |N(S)| >= 4,
  where N(S) = S \\ (intersection of all parents of S).

This is the one local bound that SURVIVES the counterexamples of
Section "Obstructions" -- only the unique-parent case can fail, and that
is exactly what verify_counterexamples.py demonstrates with CE1/CE3.
"""
import random
from fractions import Fraction as Fr

from lattice import all_pms, build_x, Nplus, parents, N_of


if __name__ == "__main__":
    print("=" * 70)
    print("Lemma [Several parents]: |Par(S)| >= 2  =>  |N(S)| >= 4")
    print("=" * 70)
    graphs = [
        (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),
        (12, [(0, 3), (0, 6), (0, 5), (1, 8), (1, 6), (1, 9), (2, 10), (2, 11),
              (2, 8), (3, 7), (3, 9), (4, 10), (4, 7), (4, 11), (5, 8), (5, 6),
              (7, 9), (10, 11)]),
    ]
    rng = random.Random(59)
    multiparent_seen = 0
    violations = 0
    instances = 0
    for n, edges in graphs:
        pms = all_pms(n, edges)
        if len(pms) < 2:
            continue
        for trial in range(25):
            k = rng.randint(1, len(pms))
            chosen = rng.sample(pms, k)
            raw = [rng.randint(1, 9) for _ in chosen]
            tot = sum(raw)
            weights = [Fr(r, tot) for r in raw]
            x = build_x(len(edges), chosen, weights)
            fam = Nplus(n, edges, x)
            instances += 1
            for S in fam:
                par = parents(S, fam)
                if len(par) >= 2:
                    multiparent_seen += 1
                    NS, _ = N_of(S, fam)
                    if len(NS) < 4:
                        violations += 1
                        print(f"  !! VIOLATION S={sorted(S)} "
                              f"|Par(S)|={len(par)} |N(S)|={len(NS)}")
    print(f"instances checked                 : {instances}")
    print(f"multi-parent non-atoms examined   : {multiparent_seen}")
    print(f"violations (|N(S)|<4)             : {violations}")
    ok = violations == 0
    print(f">>> Several-parents Lemma intact : {ok}\n")
    print("=" * 70)
    print("PASS" if ok else "FAIL")
    print("=" * 70)
