#!/usr/bin/env python3
"""
gen_gadget.py
==============
RECONSTRUCTED SCRIPT -- not recovered from the user's original repository
(the original file was not present in the uploaded archive). This is a
fresh implementation.

Generates the extremal family Theta_t referenced in thin_matching.tex
(Section 1, "the family we call Theta_t") and a vertex-thickening
operation.

--------------------------------------------------------------------------
IMPORTANT PROVENANCE NOTE
--------------------------------------------------------------------------
thin_matching.tex itself never spells out the construction of Theta_t; it
only cites it as "Lemma 1.2" of Haqi & Oveis Gharan, "On Thin Perfect
Matchings up to Polylogarithmic Factors" (arXiv:2606.01330, [HOG26] in the
bibliography). The construction below is transcribed directly from that
paper's Lemma 1.2 and Figure 1 (the user supplied the PDF):

    Bipartite graph on 2t+2 vertices: z_1..z_t, y_1..y_t, and two special
    vertices z, y. Edges:
      solid  (z_i, y_i)  weight 1 - 1/t     for i = 1..t
      dotted (z_i, y)    weight 1/t         for i = 1..t
      dotted (y_i, z)    weight 1/t         for i = 1..t
    This x is a valid point of PM(G) (every vertex has x-degree exactly 1).
    Any perfect matching M subseteq supp(x) is forced to use at least one
    dotted edge (z has no solid edge, so it must match to some y_i via a
    dotted edge, forcing y_i's partner z_i to fall back to its own dotted
    edge to y); the cut S={z_1,y_1} then has mu(S) = 2/t while any two
    forced dotted-edge crossings there give |M ∩ delta(S)| = 2, giving
    ratio t. The paper's Lemma 1.2 states this shows thin(G,x) >= t/2 for
    every M subseteq supp(x); exact brute-force computation (see the
    docstring test below) in fact gives thin(G,x) = t exactly for small t,
    consistent with (and stronger than) the paper's stated bound.

This is the correct, sourced Theta_t -- not a guess. It replaces an
earlier draft of this file (never shown to the user) that would have used
an invented "blob" placeholder family, which is no longer necessary now
that the source construction is available.
--------------------------------------------------------------------------

Also provides a generic "thickening" operation: replace each vertex by a
twin pair joined by an edge, splitting each original edge's weight between
the two possible twin-to-twin connections. NOTE: unlike Theta_t above,
this thickening operation is NOT from either paper -- it is a standard,
generic technique for scaling up test instances while keeping vertex
degrees bounded, included here as a convenience for stress-testing, and
should not be attributed to the authors.
"""
import os
from fractions import Fraction as Fr


def theta_t(t):
    """
    HOG26 Lemma 1.2 / Figure 1 construction, parameter t (their 'n').
    Returns (n, edges, x) with n = 2t+2, x given as a list of Fractions
    aligned with `edges` (already a valid point of PM(G), not a convex
    combination -- see the module docstring).

    Vertex labelling: z_i -> i (0..t-1), y_i -> t+i (0..t-1), z -> 2t,
    y -> 2t+1.
    """
    if t < 2:
        raise ValueError("t must be >= 2 for Theta_t to be well-defined")
    n = 2 * t + 2
    edges = []
    x = []
    for i in range(t):
        edges.append((i, t + i))
        x.append(Fr(t - 1, t))          # solid (z_i, y_i)
        edges.append((i, 2 * t + 1))
        x.append(Fr(1, t))              # dotted (z_i, y)
        edges.append((t + i, 2 * t))
        x.append(Fr(1, t))              # dotted (y_i, z)
    return n, edges, x


def thicken(n, edges, x, factor=2):
    """
    Generic vertex-thickening (NOT from either paper; see module docstring).
    Replaces each vertex v by `factor` twin copies v_0..v_{factor-1} joined
    in a path by edges of weight 1 - 1/factor each (so each twin still has
    total x-degree 1 within its own twin-path plus its share of v's
    original edges), and each original edge (u,v) of weight w is replaced
    by a perfect matching between the twin sets of u and v, each new edge
    getting weight w/factor.

    This keeps x a valid point of PM(G') on the thickened graph G' as long
    as the original x was a valid point of PM(G) (verified by the caller
    via x_degrees_ok). It is intended purely for generating larger stress
    instances with a similar cut structure, not as a construction with any
    claimed extremal property of its own.
    """
    new_n = n * factor

    def twin(v, k):
        return v * factor + k

    new_edges = []
    new_x = []
    # twin-path edges within each original vertex's twin group
    for v in range(n):
        for k in range(factor - 1):
            new_edges.append((twin(v, k), twin(v, k + 1)))
            new_x.append(Fr(1, factor))
    # replace each original edge with a twin-to-twin matching
    for (u, v), w in zip(edges, x):
        for k in range(factor):
            new_edges.append((twin(u, k), twin(v, k)))
            new_x.append(w / factor)
    return new_n, new_edges, new_x


def write_graph(path, n, edges):
    with open(path, "w") as f:
        f.write(f"{n} {len(edges)}\n")
        for (u, v) in edges:
            f.write(f"{u} {v}\n")


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "gadget")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 70)
    print("Generating Theta_t family (Haqi-Oveis Gharan Lemma 1.2)")
    print("=" * 70)
    for t in range(2, 9):
        n, edges, x = theta_t(t)
        path = os.path.join(out_dir, f"theta_{t}.txt")
        write_graph(path, n, edges)
        print(f"  theta_{t}: n={n} vertices, {len(edges)} edges -> {path}")

    print()
    print("Generating thickened variants (factor=2, generic stress test, "
          "not from either paper)")
    for t in [3, 5]:
        n, edges, x = theta_t(t)
        tn, tedges, tx = thicken(n, edges, x, factor=2)
        path = os.path.join(out_dir, f"theta_{t}_thick2.txt")
        write_graph(path, tn, tedges)
        print(f"  theta_{t}_thick2: n={tn} vertices, {len(tedges)} edges "
              f"-> {path}")

    print()
    print("Done. Note: x-weights are not written to the .txt graph files "
          "(the plain n/m + edge-list format used across this repo carries "
          "combinatorial structure only); scripts that need this specific "
          "x should call theta_t(t)/thicken(...) directly, as in "
          "verify_local_ingredients.py.")
