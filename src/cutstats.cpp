// cutstats.cpp
// =============
// RECONSTRUCTED FILE -- not recovered from the user's original repository
// (not present in the uploaded archive); fresh implementation matching
// the role described in README.md ("Phi-certificate, primitive-cut
// counts, atom packing, N+"). See verify/verify_parity_lemma.py's header
// comment for the general disclosure that applies to every reconstructed
// file in this repository.
//
// Usage:
//   cutstats < graph.txt
// Input format (stdin):
//   n m
//   u v w_num w_den        (m lines: edge, x-weight as a reduced fraction)
// Output (to stdout):
//   N+ (count of primitive cuts S, one side per cut avoiding vertex 0,
//       with 0 < mu(S) < 1/2)
//   number of atoms (minimal elements of that family) and their sizes
//   Phi(alpha) for alpha = n/2, n, 2n  (exact rational arithmetic)
//
// Mirrors the conventions fixed in verify/lattice.py: primitivity and
// connectivity are computed in the SUPPORT graph H = (V, supp(x)), and
// each cut is represented once, by the side avoiding vertex 0 (matching
// the paper's own convention, Section "Structure of the critical
// family" -- see also the double-counting bug found and fixed in
// lattice.py while building the Python side of this repository).

#include <bits/stdc++.h>
using namespace std;

struct Frac {
    long long num, den;
    Frac(long long n = 0, long long d = 1) {
        if (d < 0) { n = -n; d = -d; }
        long long g = std::gcd(std::abs(n), d);
        if (g == 0) g = 1;
        num = n / g; den = d / g;
    }
    Frac operator+(const Frac &o) const { return Frac(num*o.den+o.num*den, den*o.den); }
    bool operator<(const Frac &o) const { return num*o.den < o.num*den; }
    bool operator>(const Frac &o) const { return o < *this; }
    bool operator<=(const Frac &o) const { return !(o < *this); }
};
ostream &operator<<(ostream &os, const Frac &f) { os << f.num << "/" << f.den; return os; }

int n, m;
vector<array<int,2>> edges;
vector<Frac> x;
vector<int> sup;

bool connected_on(unsigned long long S, bool complement) {
    // check connectivity of the induced subgraph on S (or V\S if complement),
    // using only support edges.
    vector<int> verts;
    for (int v = 0; v < n; v++) {
        bool in_S = (S >> v) & 1;
        if (in_S != complement) verts.push_back(v);
    }
    if (verts.empty()) return false;
    map<int,vector<int>> adj;
    set<int> vset(verts.begin(), verts.end());
    for (int e : sup) {
        int a = edges[e][0], b = edges[e][1];
        if (vset.count(a) && vset.count(b)) { adj[a].push_back(b); adj[b].push_back(a); }
    }
    set<int> seen;
    vector<int> st = {verts[0]};
    seen.insert(verts[0]);
    while (!st.empty()) {
        int a = st.back(); st.pop_back();
        for (int b : adj[a]) if (!seen.count(b)) { seen.insert(b); st.push_back(b); }
    }
    return (int)seen.size() == (int)verts.size();
}

Frac cut_weight(unsigned long long S) {
    Frac mu(0);
    for (int i = 0; i < m; i++) {
        bool a_in = (S >> edges[i][0]) & 1;
        bool b_in = (S >> edges[i][1]) & 1;
        if (a_in != b_in) mu = mu + x[i];
    }
    return mu;
}

int main() {
    ios::sync_with_stdio(false);
    cin >> n >> m;
    edges.resize(m); x.resize(m);
    for (int i = 0; i < m; i++) {
        long long u, v, wn, wd;
        cin >> u >> v >> wn >> wd;
        edges[i] = {(int)u, (int)v};
        x[i] = Frac(wn, wd);
    }
    for (int i = 0; i < m; i++) if (x[i].num != 0) sup.push_back(i);

    // enumerate primitive cuts S avoiding vertex 0, 0 < mu(S) < 1/2
    vector<unsigned long long> fam;
    for (unsigned long long S = 1; S < (1ULL << (n - 1)); S++) {
        // S ranges over subsets of {1,...,n-1} by construction (bit 0 unset,
        // since S < 2^(n-1) using bits 1..n-1 -- shift left by 1 to encode)
        unsigned long long Sshift = S << 1; // vertex 0 excluded
        int popcount = __builtin_popcountll(Sshift);
        if (popcount % 2 != 0) continue;
        Frac mu = cut_weight(Sshift);
        if (!(mu.num > 0 && mu.den > 0)) continue;
        // 0 < mu < 1/2  <=>  0 < mu.num/mu.den < 1/2 <=> 2*mu.num < mu.den (and mu.num>0)
        if (!(mu.num > 0 && 2 * mu.num < mu.den)) continue;
        if (!connected_on(Sshift, false)) continue;
        if (!connected_on(Sshift, true)) continue;
        fam.push_back(Sshift);
    }

    cout << "N+ = " << fam.size() << "\n";

    // atoms: minimal elements under inclusion
    vector<unsigned long long> atoms;
    for (auto S : fam) {
        bool minimal = true;
        for (auto T : fam) {
            if (T == S) continue;
            if ((T & S) == T && T != S) { minimal = false; break; } // T subsetneq S
        }
        if (minimal) atoms.push_back(S);
    }
    cout << "atoms = " << atoms.size() << " : ";
    for (auto a : atoms) cout << "{";
    for (size_t i = 0; i < atoms.size(); i++) {
        cout << "size " << __builtin_popcountll(atoms[i]);
        if (i + 1 < atoms.size()) cout << ", ";
    }
    cout << "\n";

    // Phi(alpha) for a few alpha values, matching thin_matching.tex Sec.
    // "The Phi-certificate": k(alpha,mu) = least even integer > alpha*mu,
    // term dropped if k(alpha,mu) > n/2.
    auto k_even = [](Frac alpha_mu) -> long long {
        // alpha_mu = alpha * mu as a Frac; find least even integer > it
        long long q = alpha_mu.num / alpha_mu.den;
        if (alpha_mu.num % alpha_mu.den == 0) { /* exact */ }
        long long k = (q % 2 == 0) ? q + 2 : q + 1;
        while (Frac(k, 1) <= alpha_mu) k += 2;
        return k;
    };
    for (long long alpha_num : {n, 2 * n}) {
        // alpha = alpha_num (integer), also try n/2 (may be non-integer)
        Frac total(0);
        for (auto S : fam) {
            Frac mu = cut_weight(S);
            Frac alpha_mu = Frac(alpha_num * mu.num, mu.den);
            long long k = k_even(alpha_mu);
            if (Frac(k, 1) > Frac(n, 2)) continue;
            // term = mu / k
            total = total + Frac(mu.num, mu.den * k);
        }
        cout << "Phi(" << alpha_num << ") = " << total
             << (total < Frac(1,1) ? "  (<1, certificate applies)" : "  (>=1)")
             << "\n";
    }
    return 0;
}
