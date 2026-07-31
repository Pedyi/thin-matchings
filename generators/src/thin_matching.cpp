// thin_matching.cpp
// ===================
// RECONSTRUCTED FILE -- not recovered from the user's original repository
// (not present in the uploaded archive); fresh implementation matching
// the role described in README.md ("exact alpha*(G,x): min over matchings,
// max over all cuts"). See verify/verify_parity_lemma.py's header comment
// for the general disclosure that applies to every reconstructed file in
// this repository.
//
// Usage:
//   thin_matching < graph.txt
// Input format (stdin):
//   n m
//   u v w_num w_den        (m lines: edge, x-weight as a reduced fraction)
// Output:
//   thin(G,x) as a reduced fraction "p/q", computed EXACTLY:
//     thin(G,x) = min over perfect matchings M subseteq supp(x)
//                 of max over cuts S (0 < x(delta(S))) of
//                 |M ∩ delta(S)| / x(delta(S))
// Exact rational arithmetic throughout (no floating point), via a small
// Frac struct on 64-bit integers -- sufficient for the small instances
// (n <= ~20) this repository's verification scripts generate.
//
// WARNING: this brute-forces all perfect matchings and all 2^n cuts, so it
// is only intended for the same small-n regime as the Python verify/
// scripts (a way to cross-check them in a second, independently written
// implementation, not a scalable solver).

#include <bits/stdc++.h>
using namespace std;

struct Frac {
    long long num, den; // den > 0, gcd(|num|,den)=1
    Frac(long long n = 0, long long d = 1) {
        if (d < 0) { n = -n; d = -d; }
        long long g = std::gcd(std::abs(n), d);
        if (g == 0) g = 1;
        num = n / g; den = d / g;
    }
    Frac operator+(const Frac &o) const { return Frac(num * o.den + o.num * den, den * o.den); }
    Frac operator-(const Frac &o) const { return Frac(num * o.den - o.num * den, den * o.den); }
    Frac operator/(long long k) const { return Frac(num, den * k); }
    bool operator<(const Frac &o) const { return num * o.den < o.num * den; }
    bool operator>(const Frac &o) const { return o < *this; }
    bool operator<=(const Frac &o) const { return !(o < *this); }
    bool operator==(const Frac &o) const { return num == o.num && den == o.den; }
};

ostream &operator<<(ostream &os, const Frac &f) {
    os << f.num << "/" << f.den;
    return os;
}

int n, m;
vector<array<int,2>> edges;
vector<Frac> x; // weight per edge

// enumerate all perfect matchings restricted to edges with x_e > 0 (the
// support graph), returning each as a bitmask over edge indices (indices
// into the `sup` vector of support-edge indices).
vector<int> sup; // indices into edges[] with x_e > 0
vector<vector<int>> all_matchings; // each entry: list of sup-indices used

void backtrack_pm(vector<char> &used, vector<int> &current, int matched) {
    if (matched == n) {
        all_matchings.push_back(current);
        return;
    }
    int v = -1;
    for (int i = 0; i < n; i++) if (!used[i]) { v = i; break; }
    used[v] = 1;
    for (int idx = 0; idx < (int)sup.size(); idx++) {
        int e = sup[idx];
        int a = edges[e][0], b = edges[e][1];
        int other = (a == v) ? b : (b == v ? a : -1);
        if (other == -1 || used[other]) continue;
        used[other] = 1;
        current.push_back(idx);
        backtrack_pm(used, current, matched + 2);
        current.pop_back();
        used[other] = 0;
    }
    used[v] = 0;
}

int main() {
    ios::sync_with_stdio(false);
    cin >> n >> m;
    edges.resize(m);
    x.resize(m);
    for (int i = 0; i < m; i++) {
        long long u, v, wn, wd;
        cin >> u >> v >> wn >> wd;
        edges[i] = {(int)u, (int)v};
        x[i] = Frac(wn, wd);
    }
    for (int i = 0; i < m; i++) if (!(x[i].num == 0)) sup.push_back(i);

    vector<char> used(n, 0);
    vector<int> current;
    backtrack_pm(used, current, 0);

    if (all_matchings.empty()) {
        cerr << "No perfect matching in supp(x); thin(G,x) undefined.\n";
        return 1;
    }

    // precompute all cuts with mu(S) > 0
    vector<pair<unsigned long long, Frac>> cuts; // bitmask over vertices, weight
    for (unsigned long long S = 1; S < (1ULL << n) - 1; S++) {
        Frac mu(0);
        for (int i = 0; i < m; i++) {
            bool a_in = (S >> edges[i][0]) & 1;
            bool b_in = (S >> edges[i][1]) & 1;
            if (a_in != b_in) mu = mu + x[i];
        }
        if (!(mu.num == 0)) cuts.push_back({S, mu});
    }

    Frac best(-1, 1);
    bool have_best = false;
    for (auto &M : all_matchings) {
        Frac worst(0);
        for (auto &[S, mu] : cuts) {
            long long cross = 0;
            for (int idx : M) {
                int e = sup[idx];
                bool a_in = (S >> edges[e][0]) & 1;
                bool b_in = (S >> edges[e][1]) & 1;
                if (a_in != b_in) cross++;
            }
            // ratio = cross / mu = cross / (mu.num/mu.den) = cross*mu.den/mu.num
            Frac ratio = Frac(cross * mu.den, mu.num);
            if (worst < ratio) worst = ratio;
        }
        if (!have_best || worst < best) { best = worst; have_best = true; }
    }
    cout << best << "\n";
    return 0;
}
