#!/usr/bin/env python3
"""
test_laminarity.py
====================
RECONSTRUCTED SCRIPT -- fresh reimplementation of the "F is not laminar"
remark near the end of Section "Structure of the critical family" in
thin_matching.tex; not the user's original code (see
verify_parity_lemma.py header for full disclosure).

The paper states: "F is not laminar in general. Crossing pairs of members
exist (for example A={5,8,9,10} and B={0,2,6,7,8,9} on 12 vertices, both
of cut weight 0.4)". This is an EXISTENCE claim (a counterexample to
laminarity), not a universal one, so this script's job is to reproduce a
concrete crossing pair -- not to sweep for a positive property.

Note: the paper's example weight 0.4 does not match the CE3 instance's x
(that one has weights in ninths and thirds, not tenths), so it is evidently
from a different point x than any explicitly given elsewhere in the
recovered materials; we cannot reconstruct that exact x. Instead we
directly demonstrate non-laminarity on the recovered CE3 witness (which
independently has 37 crossing pairs, as found while building
verify_trichotomy_and_component.py) -- sufficient to prove the same
qualitative claim.
"""
import itertools
from fractions import Fraction as Fr

from lattice import build_x, edge_index, Nplus


def find_crossing_pairs(fam, limit=5):
    found = []
    for P, Q in itertools.combinations(fam, 2):
        if P & Q and P - Q and Q - P:
            found.append((P, Q))
            if len(found) >= limit:
                break
    return found


if __name__ == "__main__":
    print("=" * 70)
    print("F is NOT laminar in general (existence, not universal, claim)")
    print("=" * 70)

    n = 12
    edges = [(0, 3), (0, 6), (0, 5), (1, 8), (1, 6), (1, 9), (2, 10), (2, 11),
              (2, 8), (3, 7), (3, 9), (4, 10), (4, 7), (4, 11), (5, 8), (5, 6),
              (7, 9), (10, 11)]
    idx = edge_index(edges)

    def pm(*es):
        return [idx[frozenset(e)] for e in es]

    ce3_x = build_x(len(edges),
                     [pm((0, 3), (1, 8), (2, 10), (4, 11), (5, 6), (7, 9)),
                      pm((0, 3), (1, 6), (2, 10), (4, 11), (5, 8), (7, 9)),
                      pm((0, 3), (1, 6), (2, 11), (4, 10), (5, 8), (7, 9)),
                      pm((0, 3), (1, 9), (2, 8), (4, 7), (5, 6), (10, 11)),
                      pm((0, 6), (1, 9), (2, 10), (3, 7), (4, 11), (5, 8))],
                     [Fr(1, 9), Fr(1, 3), Fr(1, 3), Fr(1, 9), Fr(1, 9)])

    fam = Nplus(n, edges, ce3_x)
    crossing = find_crossing_pairs(fam)
    print(f"|F| on the paper's CE3 instance: {len(fam)}")
    print(f"Sample of crossing pairs found (up to 5 shown):")
    for P, Q in crossing:
        print(f"  A={sorted(P)}  B={sorted(Q)}  "
              f"A∩B={sorted(P&Q)}  A\\B={sorted(P-Q)}  B\\A={sorted(Q-P)}")
    ok = len(crossing) > 0
    print(f"\n>>> F fails to be laminar on this instance : {ok}")
    print("(The paper's own worked example, A={5,8,9,10}, "
          "B={0,2,6,7,8,9}, weight 0.4, uses a different x than any "
          "recovered in the uploaded materials and could not be "
          "reconstructed; the instance above independently establishes "
          "the same qualitative fact -- F is not laminar in general.)\n")
    print("=" * 70)
    print("PASS" if ok else "FAIL")
    print("=" * 70)
