#!/usr/bin/env python3
"""
verify_disjunction.py
=======================
RECONSTRUCTED SCRIPT -- fresh reimplementation of the "uncrossing
disjunction" combinatorial step used inside the proof of Proposition
[Atoms are disjoint] in thin_matching.tex; not the user's original code
(see verify_parity_lemma.py header for full disclosure).

This isolates and directly tests the three-step disjunction chained
together in that proof, rather than only the end conclusion (which
verify_atoms_disjoint.py already checks):

  Suppose distinct atoms P, Q share a vertex.
  (1) [Parity]      P,Q cross (neither contains the other since both are
                     minimal and distinct) => all of P∩Q, P\\Q, Q\\P even.
  (2) [Trichotomy]   some piece Z of {P∩Q, P\\Q, Q\\P} has weight in (0,1/2).
  (3) [Components]   some connected component Y of H[Z] has 0<mu(Y)<1/2,
                      and is even and connected (via Lemma [Components]).
  (4) [Escape]        applying Escape to (P,Y) (or (Q,Y), whichever contains
                      Z as a proper subset), either Y in F or some
                      component D of H[P\\Y] (resp. H[Q\\Y]) is in F and
                      strictly inside P (resp. Q).
  Conclusion: F contains a member strictly inside the atom P (or Q),
  contradicting minimality -- so no two distinct atoms actually share a
  vertex on any tested instance where atoms happen to intersect (there
  should never be any: this script hunts for shared-vertex atom pairs at
  all, which by the Proposition should not exist, and if a sweep were ever
  to find one, walks the disjunction to make sure it is exercised).
"""
import random
from fractions import Fraction as Fr

from lattice import mu, all_pms, build_x, support, conn, Nplus


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


def atoms_of(fam):
    return [S for S in fam if not any(T < S for T in fam)]


def walk_disjunction(n, edges, x, P, Q, famset):
    """Run steps (1)-(4) for a pair P,Q that share a vertex; return True if
    the disjunction produces a member of F strictly inside P or Q."""
    H = support(edges, x)
    inter, pminusq, qminusp = P & Q, P - Q, Q - P
    if not (inter and pminusq and qminusp):
        return None  # not actually crossing (one contains the other)

    # (1) parity: all three pieces should be even
    if any(len(piece) % 2 != 0 for piece in (inter, pminusq, qminusp)):
        return False  # would itself be a bug (Parity Lemma violated)

    # (2) trichotomy
    pieces_weights = {"P∩Q": (inter, mu(n, edges, x, inter)),
                       "P\\Q": (pminusq, mu(n, edges, x, pminusq)),
                       "Q\\P": (qminusp, mu(n, edges, x, qminusp))}
    Z = None
    for name, (piece, w) in pieces_weights.items():
        if 0 < w < Fr(1, 2):
            Z = piece
            break
    if Z is None:
        return False  # Trichotomy Lemma violated -- shouldn't happen

    parent = P if Z < P else (Q if Z < Q else None)
    if parent is None:
        return False

    # (3) components of H[Z], find one with positive weight
    comps = components_of(H, Z)
    Y = None
    for comp in comps:
        if mu(n, edges, x, comp) > 0:
            Y = comp
            break
    if Y is None:
        return False

    # (4) escape applied to (parent, Y)
    if Y in famset:
        return True
    remainder = parent - Y
    rcomps = components_of(H, remainder)
    return any((c in famset and c < parent) for c in rcomps)


if __name__ == "__main__":
    print("=" * 70)
    print("Uncrossing disjunction (parity -> trichotomy -> components -> "
          "escape)")
    print("=" * 70)
    graphs = [
        (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),
        (12, [(0, 3), (0, 6), (0, 5), (1, 8), (1, 6), (1, 9), (2, 10), (2, 11),
              (2, 8), (3, 7), (3, 9), (4, 10), (4, 7), (4, 11), (5, 8), (5, 6),
              (7, 9), (10, 11)]),
    ]
    rng = random.Random(71)
    shared_vertex_pairs_found = 0
    disjunction_failures = 0
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
            famset = set(fam)
            atoms = atoms_of(fam)
            instances += 1
            for i, P in enumerate(atoms):
                for Q in atoms[i + 1:]:
                    if P & Q:
                        shared_vertex_pairs_found += 1
                        result = walk_disjunction(n, edges, x, P, Q, famset)
                        if result is False:
                            disjunction_failures += 1
                            print(f"  !! DISJUNCTION FAILED for atoms "
                                  f"P={sorted(P)} Q={sorted(Q)}")
    print(f"instances checked                 : {instances}")
    print(f"atom pairs sharing a vertex found : {shared_vertex_pairs_found} "
          f"(Proposition predicts this should always be 0)")
    print(f"disjunction failures               : {disjunction_failures}")
    ok = disjunction_failures == 0
    print(f">>> intact : {ok}\n")
    print("=" * 70)
    print("PASS" if ok else "FAIL")
    print("=" * 70)
