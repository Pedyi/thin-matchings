#!/usr/bin/env python3
"""
verify_hall_condition.py
==========================
RECONSTRUCTED SCRIPT -- fresh reimplementation checking Hall's condition
directly, as evidence related to Proposition [Double counting] in
thin_matching.tex; not the user's original code (see
verify_parity_lemma.py header for full disclosure).

Proposition [Double counting] gives a SUFFICIENT condition (constants
k>=t with |N(S)|>=k for every non-atom and every vertex in at most t
non-atoms' N(S)) for Hall's condition |N(J)| >= |J| to hold for every set
J of non-atoms, which would give an injective system of distinct
representatives and hence N+ = O(n).

Section "Obstructions" shows the sufficient condition (k>=t) FAILS on two
explicit witnesses. This script checks something logically weaker and
directly informative: does Hall's condition ITSELF still hold on those
same witnesses and on further random instances, even though the
sufficient (k,t) route to it is broken? A "yes" everywhere tested would be
mild evidence *for* the main open conjecture via a route other than
Proposition [Double counting]; a "no" would be a genuine new obstruction
worth flagging. (The paper does not claim either way about Hall's
condition itself, only about the k>=t sufficient condition -- this check
is included as an evidence-gathering tool per the README's own
"Lemma -> script" table entry "Hall condition (evidence)".)
"""
import itertools
from fractions import Fraction as Fr

from lattice import build_x, edge_index, Nplus, parents, N_of


def non_atoms_and_N(fam):
    result = {}
    for S in fam:
        par = parents(S, fam)
        if not par:
            continue  # atom
        NS, _ = N_of(S, fam)
        result[S] = NS
    return result


def hall_holds(non_atom_N):
    """Brute force over all subsets J of non-atoms (feasible for small |F|).
    Returns (holds: bool, first violating J or None)."""
    items = list(non_atom_N.items())
    m = len(items)
    for r in range(1, m + 1):
        for comb in itertools.combinations(range(m), r):
            J = [items[i][0] for i in comb]
            NJ = set()
            for i in comb:
                NJ |= items[i][1]
            if len(NJ) < len(J):
                return False, J
    return True, None


if __name__ == "__main__":
    print("=" * 70)
    print("Hall's condition on non-atoms of F  (evidence-gathering, not a "
          "proof either way)")
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
    naN = non_atoms_and_N(fam)
    holds, bad = hall_holds(naN)
    print(f"Paper's CE3 instance (known k>=t sufficient condition FAILS "
          f"here, k=2<t=3): Hall's condition itself holds = {holds}")
    if not holds:
        print(f"  violating J: {[sorted(S) for S in bad]}")

    import random
    rng = random.Random(101)
    from lattice import all_pms
    graphs = [
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),
    ]
    total = 0
    fails = 0
    for gn, ge in graphs:
        pms = all_pms(gn, ge)
        for trial in range(15):
            k = rng.randint(1, len(pms))
            chosen = rng.sample(pms, k)
            raw = [rng.randint(1, 9) for _ in chosen]
            tot_w = sum(raw)
            weights = [Fr(r, tot_w) for r in raw]
            x = build_x(len(ge), chosen, weights)
            fam2 = Nplus(gn, ge, x)
            naN2 = non_atoms_and_N(fam2)
            if not naN2:
                continue
            total += 1
            h, b = hall_holds(naN2)
            if not h:
                fails += 1
                print(f"  !! HALL CONDITION FAILS on random instance n={gn}"
                      f", violating J={[sorted(S) for S in b]}")
    print(f"\nrandom instances with >=1 non-atom checked : {total}")
    print(f"Hall-condition failures on those            : {fails}")
    print("(This script gathers evidence only; neither outcome proves or "
          "disproves Open Problem [Main].)\n")
    print("=" * 70)
    print("DONE (informational -- see notes above; not a pass/fail check "
          "of a claim in the paper)")
    print("=" * 70)
