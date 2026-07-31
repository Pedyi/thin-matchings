#!/usr/bin/env python3
"""
measure_width_height.py
=========================
RECONSTRUCTED SCRIPT -- fresh reimplementation motivated by the remark
in thin_matching.tex, Section "Structure of the critical family":
  "So the poset (F, subseteq) has at most n/2 minimal elements (atoms) and
  height at most n/2. Mirsky's theorem gives N+ <= width x height, which
  is only quadratic."
Not the user's original code (see verify_parity_lemma.py header for full
disclosure).

Measures, for random instances: |F| (=N+), the poset width (size of the
largest antichain, via Dilworth/Mirsky -- computed here by a direct
maximum-antichain search, feasible since the instances are small), and the
poset height (longest chain), and reports how the quadratic bound
width*height compares to the actual N+ and to the linear target n.
"""
import itertools
import random
from fractions import Fraction as Fr

from lattice import all_pms, build_x, Nplus


def longest_chain(fam):
    fam_sorted = sorted(fam, key=len)
    best = {S: 1 for S in fam_sorted}
    for i, S in enumerate(fam_sorted):
        for T in fam_sorted[:i]:
            if T < S and best[T] + 1 > best[S]:
                best[S] = best[T] + 1
    return max(best.values()) if best else 0


def max_antichain_size(fam):
    """Brute force: an antichain is a set of pairwise-incomparable members.
    Feasible for the small |F| produced on these instances."""
    fam = list(fam)
    m = len(fam)
    if m == 0:
        return 0
    incomparable = [[not (fam[i] < fam[j] or fam[j] < fam[i])
                      for j in range(m)] for i in range(m)]
    best = 0
    # simple branch and bound over subsets, order by index to avoid dup work
    def backtrack(start, current):
        nonlocal best
        best = max(best, len(current))
        for k in range(start, m):
            if all(incomparable[k][c] for c in current):
                current.append(k)
                backtrack(k + 1, current)
                current.pop()
    backtrack(0, [])
    return best


if __name__ == "__main__":
    print("=" * 70)
    print("Poset (F, subseteq) width/height measurements vs N+ and n")
    print("=" * 70)
    graphs = [
        (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        (8, [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (2, 6), (2, 3), (3, 7),
             (4, 6), (4, 5), (5, 7), (6, 7)]),
        (12, [(0, 3), (0, 6), (0, 5), (1, 8), (1, 6), (1, 9), (2, 10), (2, 11),
              (2, 8), (3, 7), (3, 9), (4, 10), (4, 7), (4, 11), (5, 8), (5, 6),
              (7, 9), (10, 11)]),
    ]
    rng = random.Random(83)
    rows = []
    for n, edges in graphs:
        pms = all_pms(n, edges)
        if len(pms) < 2:
            continue
        for trial in range(15):
            k = rng.randint(1, len(pms))
            chosen = rng.sample(pms, k)
            raw = [rng.randint(1, 9) for _ in chosen]
            tot = sum(raw)
            weights = [Fr(r, tot) for r in raw]
            x = build_x(len(edges), chosen, weights)
            fam = Nplus(n, edges, x)
            Np = len(fam)
            height = longest_chain(fam)
            width = max_antichain_size(fam)
            rows.append((n, Np, width, height, width * height))

    print(f"{'n':>4} {'N+':>4} {'width':>6} {'height':>7} "
          f"{'width*height':>13} {'N+ / n':>8}")
    max_np_over_n = Fr(0)
    for n, Np, w, h, wh in rows:
        ratio = Fr(Np, n)
        if ratio > max_np_over_n:
            max_np_over_n = ratio
        print(f"{n:>4} {Np:>4} {w:>6} {h:>7} {wh:>13} {str(ratio):>8}")

    print(f"\nmax observed N+/n over this sweep : {max_np_over_n}")
    print("(Open Problem [Main]: is N+ = O(n) for every G, x? This sweep's "
          "own random instances are not the same sweep the paper's README "
          "describes (which reports max N+/n observed <= 1 on its much "
          "larger instance library); here the ratio can exceed 1 on some "
          "small random instances, which is still perfectly consistent "
          "with N+ = O(n) -- only a ratio growing without bound as n grows "
          "would be evidence against the conjecture, and this sweep is too "
          "small to say anything about that trend either way.)")
