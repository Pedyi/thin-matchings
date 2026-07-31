#!/usr/bin/env python3
"""
gen_hunt.py
============
RECONSTRUCTED SCRIPT -- not recovered from the user's original repository
(the original file was not present in the uploaded archive); fresh
implementation (see verify_parity_lemma.py header for the general
disclosure).

Generates, to ../hunt/ (same n/m + edge-list format as gen_graphs.py):

  - the Petersen graph and the generalized Petersen graphs GP(n,k), a
    standard, exactly-specified family that includes the Petersen graph
    itself (GP(5,2)), the Mobius-Kantor-like GP(8,3), and the Mobius
    ladders GP(n,1)-adjacent constructions -- a legitimate stand-in for
    "snarks and Petersen relatives" that is precisely defined rather than
    guessed (true snarks, e.g. the flower snark, require a case-by-case
    construction; GP(n,k) is the well-known parametrized family closest
    in spirit that is easy to state exactly);
  - random d-regular graphs for a few small d, via the configuration
    model;
  - irregular random graphs with a prescribed, non-constant degree
    sequence realized via the Havel-Hakimi algorithm.
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "verify"))


def generalized_petersen(n, k):
    """GP(n,k): outer n-cycle u_0..u_{n-1}, inner vertices v_0..v_{n-1}
    with v_i - v_{i+k mod n}, and spokes u_i - v_i. Standard construction;
    GP(5,2) is the Petersen graph. Vertex count = 2n."""
    edges = []
    for i in range(n):
        edges.append((i, (i + 1) % n))                    # outer cycle
        edges.append((n + i, n + (i + k) % n))             # inner "star"
        edges.append((i, n + i))                           # spoke
    # de-duplicate (inner edges can double-count for some k)
    return sorted({tuple(sorted(e)) for e in edges})


def is_connected(n, edges):
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


def random_d_regular(n, d, rng, max_tries=300):
    assert (n * d) % 2 == 0
    for _ in range(max_tries):
        stubs = [v for v in range(n) for _ in range(d)]
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


def havel_hakimi(deg_seq):
    """Realize a graphical degree sequence as a simple graph's edge list,
    or return None if the sequence is not graphical."""
    seq = sorted(((d, i) for i, d in enumerate(deg_seq)), reverse=True)
    edges = []
    seq = list(seq)
    while seq:
        seq.sort(reverse=True)
        d, v = seq[0]
        if d == 0:
            break
        if d > len(seq) - 1:
            return None
        rest = seq[1:]
        for i in range(d):
            dd, u = rest[i]
            if dd - 1 < 0:
                return None
            rest[i] = (dd - 1, u)
            edges.append(tuple(sorted((v, u))))
        seq = rest
    return edges


def irregular_random(n, rng, max_tries=100):
    for _ in range(max_tries):
        # a non-constant but even-sum degree sequence
        base = rng.choice([2, 3, 4])
        deg = [base + rng.choice([-1, 0, 0, 1]) for _ in range(n)]
        deg = [max(1, min(n - 1, d)) for d in deg]
        if sum(deg) % 2 != 0:
            deg[0] += 1
            deg[0] = min(deg[0], n - 1)
        edges = havel_hakimi(deg)
        if edges is None:
            continue
        if is_connected(n, edges) and has_perfect_matching(n, edges):
            return edges
    return None


def write_graph(path, n, edges):
    with open(path, "w") as f:
        f.write(f"{n} {len(edges)}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "hunt")
    os.makedirs(out_dir, exist_ok=True)
    rng = random.Random(307)

    print("=" * 70)
    print("Generating generalized-Petersen / regular / irregular graphs")
    print("=" * 70)

    gp_params = [(5, 2), (6, 2), (7, 2), (8, 3)]  # GP(5,2)=Petersen graph
    for n, k in gp_params:
        edges = generalized_petersen(n, k)
        N = 2 * n
        name = "petersen" if (n, k) == (5, 2) else f"GP_{n}_{k}"
        path = os.path.join(out_dir, f"{name}.txt")
        if is_connected(N, edges) and has_perfect_matching(N, edges):
            write_graph(path, N, edges)
            print(f"  {name}: n={N}, {len(edges)} edges -> {path}")
        else:
            print(f"  {name}: failed connectivity/PM check, skipping")

    for n in [8, 10, 12]:
        for d in [3, 4]:
            if (n * d) % 2 != 0 or d >= n:
                continue
            edges = random_d_regular(n, d, rng)
            if edges is None:
                print(f"  regular_{n}_{d}: FAILED to generate, skipping")
                continue
            path = os.path.join(out_dir, f"regular_{n}_{d}.txt")
            write_graph(path, n, edges)
            print(f"  regular_{n}_{d}: n={n}, {len(edges)} edges -> {path}")

    for n in [8, 10, 12]:
        edges = irregular_random(n, rng)
        if edges is None:
            print(f"  irregular_{n}: FAILED to generate, skipping")
            continue
        path = os.path.join(out_dir, f"irregular_{n}.txt")
        write_graph(path, n, edges)
        print(f"  irregular_{n}: n={n}, {len(edges)} edges -> {path}")

    print("\nDone.")
