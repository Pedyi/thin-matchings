#!/usr/bin/env python3
"""
lattice.py
==========
Shared brute-force helpers used by all verification scripts.

Provides:
  all_pms(n, edges)          -- enumerate all perfect matchings (as edge-index lists)
  Nplus(n, edges, x)         -- compute F = {primitive S: 0 < mu(S) < 1/2}
  mu(n, edges, x, S)         -- cut weight of S under x
  support(edges, x)          -- edges with positive weight
  conn(sub_edges, S)         -- connectivity check in subgraph
  parents(S, fam)            -- maximal members of fam strictly below S
  N_of(S, fam)               -- increment N(S) and parent list
  x_degrees_ok(n, edges, x)  -- check x is in PM(G) (all x-degrees = 1)
  build_x(m, pm_edge_sets, weights) -- build x as convex combination
  edge_index(edges)          -- map frozenset(e) -> index
  load_graph(path)           -- load graph from text file (n m / edges)
"""

import itertools
from fractions import Fraction as Fr

# ------------------------------------------------------------------ helpers --

def mu(n, edges, x, S):
    S = set(S)
    return sum(x[i] for i, (u, v) in enumerate(edges) if (u in S) != (v in S))


def support(edges, x):
    return [e for e, w in zip(edges, x) if w > 0]


def conn(sub_edges, S):
    S = set(S)
    if not S:
        return False
    adj = {v: [] for v in S}
    for (u, v) in sub_edges:
        if u in S and v in S:
            adj[u].append(v)
            adj[v].append(u)
    st = [next(iter(S))]
    seen = {st[0]}
    while st:
        a = st.pop()
        for b in adj[a]:
            if b not in seen:
                seen.add(b)
                st.append(b)
    return len(seen) == len(S)


def is_primitive(n, H, S):
    """S is primitive: even, nonempty proper, both S and V\\S connected in H."""
    S = set(S)
    if len(S) % 2 != 0 or len(S) == 0 or len(S) == n:
        return False
    return conn(H, S) and conn(H, set(range(n)) - S)


def primitive_cuts_one_sided(n, edges, x, weight_min=None, weight_max=None):
    """
    All primitive cuts S, ONE representative per cut (the side avoiding
    vertex 0), matching the paper's convention (Section "Structure of the
    critical family": "after choosing, for each cut, the side avoiding a
    fixed root vertex"). Without this restriction, both S and V\\S would be
    emitted for the same cut (since mu(S) = mu(V\\S) always), silently
    doubling any sum or count taken over the result.

    weight_min / weight_max (Fractions), if given, filter by mu(S) in
    (weight_min, weight_max) with the same open/closed convention as the
    caller needs; pass None to skip a bound.
    """
    H = support(edges, x)
    fam = []
    for r in range(2, n, 2):
        for comb in itertools.combinations(range(1, n), r):
            # vertex 0 excluded from S by construction (range starts at 1)
            S = frozenset(comb)
            if not is_primitive(n, H, S):
                continue
            mS = mu(n, edges, x, S)
            if weight_min is not None and not (mS > weight_min):
                continue
            if weight_max is not None and not (mS < weight_max):
                continue
            fam.append(S)
    return fam


def Nplus(n, edges, x):
    """F = { primitive even S (avoiding vertex 0), 0 < mu(S) < 1/2 }."""
    return primitive_cuts_one_sided(n, edges, x,
                                     weight_min=Fr(0), weight_max=Fr(1, 2))


def parents(S, fam):
    below = [T for T in fam if T < S]
    return [T for T in below if not any(T < U for U in below)]


def N_of(S, fam):
    par = parents(S, fam)
    if not par:
        return set(), []
    inter = set(par[0])
    for P in par[1:]:
        inter &= set(P)
    return set(S) - inter, par


def x_degrees_ok(n, edges, x):
    deg = [Fr(0)] * n
    for (u, v), w in zip(edges, x):
        deg[u] += w
        deg[v] += w
    return all(d == 1 for d in deg), deg


def build_x(m, pm_edge_sets, weights):
    """x = sum_j weights[j] * indicator(pm_j). weights must sum to 1."""
    x = [Fr(0)] * m
    for w, pm in zip(weights, pm_edge_sets):
        for i in pm:
            x[i] += w
    return x


def edge_index(edges):
    return {frozenset(e): i for i, e in enumerate(edges)}


def all_pms(n, edges):
    """
    Enumerate all perfect matchings of the graph (n vertices, edge list).
    Returns a list of lists, each list being the edge indices of one PM.
    Only feasible for small n (n <= 16 or so).
    """
    if n % 2 != 0:
        return []
    idx = edge_index(edges)
    results = []

    def backtrack(remaining_vertices, chosen_edges):
        if not remaining_vertices:
            results.append(list(chosen_edges))
            return
        v = min(remaining_vertices)
        for i, (u, w) in enumerate(edges):
            if i in chosen_edges:
                continue
            if u == v and w in remaining_vertices:
                backtrack(remaining_vertices - {v, w}, chosen_edges | {i})
            elif w == v and u in remaining_vertices:
                backtrack(remaining_vertices - {v, u}, chosen_edges | {i})

    backtrack(set(range(n)), set())
    return results


def load_graph(path):
    """
    Load a graph from a text file.
    Format: first line is "n m", then m lines each "u v".
    Returns (n, edges) where edges is a list of (u,v) pairs.
    """
    with open(path) as f:
        parts = f.readline().split()
        n, m = int(parts[0]), int(parts[1])
        edges = []
        for _ in range(m):
            p = f.readline().split()
            edges.append((int(p[0]), int(p[1])))
    return n, edges
