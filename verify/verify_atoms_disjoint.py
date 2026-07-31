#!/usr/bin/env python3
"""
verify_atoms_disjoint.py
==========================
RECONSTRUCTED SCRIPT -- fresh reimplementation from Proposition [Atoms are
disjoint] in thin_matching.tex; not the user's original code (see
verify_parity_lemma.py header for full disclosure).

Checks Proposition [Atoms are disjoint]:
  Distinct atoms (minimal members) of F = {primitive S : 0<mu(S)<1/2} are
  pairwise vertex-disjoint. Consequently |atoms| <= n/2 (Corollary).
"""
import random
from fractions import Fraction as Fr

from lattice import all_pms, build_x, Nplus


def atoms_of(fam):
    return [S for S in fam if not any(T < S for T in fam)]


def check_instance(n, edges, x):
    fam = Nplus(n, edges, x)
    atoms = atoms_of(fam)
    violations = 0
    for A, B in [(a, b) for i, a in enumerate(atoms)
                 for b in atoms[i + 1:]]:
        if A & B:
            violations += 1
            print(f"  !! ATOMS SHARE VERTICES: {sorted(A)} and {sorted(B)}")
    count_ok = len(atoms) <= n // 2
    if not count_ok:
        print(f"  !! ATOM COUNT EXCEEDS n/2: {len(atoms)} atoms on n={n}")
    return len(atoms), violations, count_ok


if __name__ == "__main__":
    print("=" * 70)
    print("Proposition: atoms of F are pairwise disjoint  (=> at most n/2)")
    print("=" * 70)
    graphs = [
        (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),
        (12, [(0, 3), (0, 6), (0, 5), (1, 8), (1, 6), (1, 9), (2, 10), (2, 11),
              (2, 8), (3, 7), (3, 9), (4, 10), (4, 7), (4, 11), (5, 8), (5, 6),
              (7, 9), (10, 11)]),
    ]
    rng = random.Random(41)
    total_viol = 0
    total_count_fail = 0
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
            na, v, cok = check_instance(n, edges, x)
            instances += 1
            total_viol += v
            if not cok:
                total_count_fail += 1
    print(f"instances checked            : {instances}")
    print(f"atom-sharing violations      : {total_viol}")
    print(f"atom-count(>n/2) violations  : {total_count_fail}")
    ok = (total_viol == 0 and total_count_fail == 0)
    print(f">>> Atoms disjoint / <=n/2 intact : {ok}\n")
    print("=" * 70)
    print("PASS" if ok else "FAIL")
    print("=" * 70)
