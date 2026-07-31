// xsearch.cpp
// ============
// RECONSTRUCTED FILE -- not recovered from the user's original repository
// (not present in the uploaded archive); fresh implementation matching
// the role described in README.md ("max over x in PM(G) of alpha*(G,x)
// (finds worst-case x)"). See verify/verify_parity_lemma.py's header
// comment for the general disclosure that applies to every reconstructed
// file in this repository.
//
// Usage:
//   xsearch < graph.txt
// Input format (stdin):
//   n m
//   u v            (m lines: plain edge list, unweighted graph)
// Behavior:
//   Enumerates all perfect matchings of G (the whole graph is the
//   candidate edge set here, not a fixed support), then does a local
//   search over convex combinations x = sum_j lambda_j M_j (lambda on a
//   coordinate grid) to look for a point x approximately maximizing
//   thin(G,x). This is a HEURISTIC search (coordinate ascent with random
//   restarts), not an exact solver -- exactly maximizing thin(G,x) over
//   the whole polytope PM(G) is itself a hard combinatorial optimization
//   problem with no known efficient exact algorithm used in this
//   repository. Intended for small n (<=10-12) as a companion to the
//   Python random-sweep scripts in verify/, to see whether a directed
//   local search finds worse (larger thin(G,x)) points than uniform
//   random sampling does.
//
// Output: best lambda vector found (one weight per perfect matching,
// index-aligned with the order matchings were enumerated) and the
// resulting thin(G,x) as a decimal approximation (floating point is used
// here, not exact rationals, since this is a heuristic search rather than
// a certifying computation -- use thin_matching.cpp on the resulting x
// for an exact, certified value).

#include <bits/stdc++.h>
using namespace std;

int n, m;
vector<array<int,2>> edges;
vector<vector<int>> all_matchings; // each: list of edge indices

void backtrack_pm(vector<char> &used, vector<int> &current, int matched) {
    if (matched == n) { all_matchings.push_back(current); return; }
    int v = -1;
    for (int i = 0; i < n; i++) if (!used[i]) { v = i; break; }
    used[v] = 1;
    for (int e = 0; e < m; e++) {
        int a = edges[e][0], b = edges[e][1];
        int other = (a == v) ? b : (b == v ? a : -1);
        if (other == -1 || used[other]) continue;
        used[other] = 1;
        current.push_back(e);
        backtrack_pm(used, current, matched + 2);
        current.pop_back();
        used[other] = 0;
    }
    used[v] = 0;
}

// given lambda (convex weights over all_matchings), compute x_e for every
// edge, then compute thin(G,x) = min over M subseteq supp(x) [approx: over
// ALL enumerated matchings, restricted to those fully inside supp(x)] of
// max over cuts S with x(delta(S))>0 of |M ∩ delta(S)| / x(delta(S)).
double eval_thin(const vector<double> &lambda) {
    vector<double> x(m, 0.0);
    for (size_t j = 0; j < all_matchings.size(); j++)
        for (int e : all_matchings[j]) x[e] += lambda[j];

    vector<pair<unsigned long long,double>> cuts;
    for (unsigned long long S = 1; S < (1ULL << n) - 1; S++) {
        double mu = 0;
        for (int e = 0; e < m; e++) {
            bool a_in = (S >> edges[e][0]) & 1;
            bool b_in = (S >> edges[e][1]) & 1;
            if (a_in != b_in) mu += x[e];
        }
        if (mu > 1e-12) cuts.push_back({S, mu});
    }

    double best = -1;
    bool have = false;
    for (auto &M : all_matchings) {
        bool inside_supp = true;
        for (int e : M) if (x[e] < 1e-12) { inside_supp = false; break; }
        if (!inside_supp) continue;
        double worst = 0;
        for (auto &[S, mu] : cuts) {
            int cross = 0;
            for (int e : M) {
                bool a_in = (S >> edges[e][0]) & 1;
                bool b_in = (S >> edges[e][1]) & 1;
                if (a_in != b_in) cross++;
            }
            double ratio = cross / mu;
            worst = max(worst, ratio);
        }
        if (!have || worst < best) { best = worst; have = true; }
    }
    return have ? best : -1.0; // -1 if no matching lies fully in supp(x)
}

int main() {
    ios::sync_with_stdio(false);
    cin >> n >> m;
    edges.resize(m);
    for (auto &e : edges) cin >> e[0] >> e[1];

    vector<char> used(n, 0);
    vector<int> current;
    backtrack_pm(used, current, 0);
    int k = all_matchings.size();
    if (k == 0) {
        cerr << "No perfect matching found.\n";
        return 1;
    }
    cerr << "Enumerated " << k << " perfect matchings.\n";

    mt19937 rng(12345);
    uniform_real_distribution<double> U(0.0, 1.0);

    vector<double> best_lambda(k, 1.0 / k);
    double best_val = eval_thin(best_lambda);

    const int RESTARTS = 8, ITERS = 300;
    for (int r = 0; r < RESTARTS; r++) {
        vector<double> lambda(k);
        double tot = 0;
        for (auto &l : lambda) { l = U(rng); tot += l; }
        for (auto &l : lambda) l /= tot;

        double cur_val = eval_thin(lambda);
        for (int it = 0; it < ITERS; it++) {
            int i = rng() % k, j = rng() % k;
            if (i == j) continue;
            double step = 0.05 * U(rng);
            step = min(step, lambda[j]);
            vector<double> cand = lambda;
            cand[i] += step; cand[j] -= step;
            double v = eval_thin(cand);
            if (v > cur_val) { lambda = cand; cur_val = v; }
        }
        if (cur_val > best_val) { best_val = cur_val; best_lambda = lambda; }
    }

    cerr << "Best thin(G,x) found (heuristic, floating point): "
         << best_val << "\n";
    cout << "lambda:";
    for (double l : best_lambda) cout << " " << l;
    cout << "\n";
    cout << "thin_approx: " << best_val << "\n";
    return 0;
}
