#!/usr/bin/env python3
"""
gen_graphs.py
==============
RECONSTRUCTED SCRIPT -- not recovered from the user's original repository
(the original file was not present in the uploaded archive); this is a
fresh implementation (see verify_parity_lemma.py header for the general
disclosure that applies to every reconstructed file in this repository).

Generates three families of even-order graphs, written to ../graphs/ in
the plain "n m / edge list" text format used across this repo
(lattice.load_graph):

  - random cubic (3-regular) graphs via the configuration model, retried
    until simple and connected;
  - "planar-ish" graphs: a triangulated strip (stacked triangles), which
    is planar by construction, plus a few random diagonals removed/added
    while preserving planarity is NOT attempted here (true planarity
    testing is out of scope) -- these are graphs of bounded degree and
    genuinely planar by construction (a maximal outerplanar-style strip),
    not a random sample from the class of all planar graphs;
  - dense random G(n,m) graphs (Erdos-Renyi-style, high edge density),
    retried until they admit at least one perfect matching (checked via a
    greedy/backtracking search on small n).

All generated graphs have even order (perfect matchings need this) and
are checked for connectivity and existence of at least one perfect
matching before being written out.
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "verify"))
from lattice import all_pms  # noqa: E402


def is_connected(n, edges):
    if n == 0:
        return True
    adj = {v: [] for v in range(n)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = {0}
    st = [0]
    while st:
        a = st.pop()
        for b in adj[a]:
            if b not in seen:
                seen.add(b)
                st.append(b)
    return len(seen) == n


def has_perfect_matching(n, edges, cap=200000):
    """Cheap existence check via bounded backtracking (not full all_pms)."""
    adj = {v: [] for v in range(n)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    counter = [0]

    def backtrack(remaining):
        if not remaining:
            return True
        counter[0] += 1
        if counter[0] > cap:
            return False
        v = min(remaining)
        for u in adj[v]:
            if u in remaining:
                if backtrack(remaining - {v, u}):
                    return True
        return False

    return backtrack(frozenset(range(n)))


def random_cubic(n, rng, max_tries=200):
    """Configuration model, 3-regular, retried until simple + connected."""
    assert n % 2 == 0 and (3 * n) % 2 == 0
    for _ in range(max_tries):
        stubs = [v for v in range(n) for _ in range(3)]
        rng.shuffle(stubs)
        pairs = list(zip(stubs[0::2], stubs[1::2]))
        edge_set = set()
        ok = True
        for u, v in pairs:
            if u == v or frozenset((u, v)) in edge_set:
                ok = False
                break
            edge_set.add(frozenset((u, v)))
        if not ok:
            continue
        edges = [tuple(sorted(e)) for e in edge_set]
        if is_connected(n, edges) and has_perfect_matching(n, edges):
            return edges
    return None


def triangulated_strip(n):
    """A planar graph by construction: a strip of n/2 stacked triangles
    (two rows of n/2 vertices each, zig-zag connected)."""
    assert n % 2 == 0
    half = n // 2
    top = list(range(half))
    bot = list(range(half, n))
    edges = []
    for i in range(half - 1):
        edges.append((top[i], top[i + 1]))
        edges.append((bot[i], bot[i + 1]))
    for i in range(half):
        edges.append((top[i], bot[i]))
    for i in range(half - 1):
        edges.append((top[i], bot[i + 1]))
    return edges


def dense_random(n, rng, density=0.6, max_tries=200):
    all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    m_target = int(density * len(all_pairs))
    for _ in range(max_tries):
        edges = rng.sample(all_pairs, m_target)
        if is_connected(n, edges) and has_perfect_matching(n, edges):
            return edges
    return None


def write_graph(path, n, edges):
    with open(path, "w") as f:
        f.write(f"{n} {len(edges)}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "graphs")
    os.makedirs(out_dir, exist_ok=True)
    rng = random.Random(211)

    print("=" * 70)
    print("Generating cubic / planar-strip / dense graph families")
    print("=" * 70)

    for n in [6, 8, 10, 12, 14]:
        edges = random_cubic(n, rng)
        if edges is None:
            print(f"  cubic_{n}: FAILED to generate, skipping")
            continue
        path = os.path.join(out_dir, f"cubic_{n}.txt")
        write_graph(path, n, edges)
        print(f"  cubic_{n}: n={n}, {len(edges)} edges -> {path}")

    for n in [6, 8, 10, 12]:
        edges = triangulated_strip(n)
        path = os.path.join(out_dir, f"planarstrip_{n}.txt")
        write_graph(path, n, edges)
        print(f"  planarstrip_{n}: n={n}, {len(edges)} edges -> {path}")

    for n in [6, 8, 10]:
        edges = dense_random(n, rng)
        if edges is None:
            print(f"  dense_{n}: FAILED to generate, skipping")
            continue
        path = os.path.join(out_dir, f"dense_{n}.txt")
        write_graph(path, n, edges)
        print(f"  dense_{n}: n={n}, {len(edges)} edges -> {path}")

    print("\nDone.")
