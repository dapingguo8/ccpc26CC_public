#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Equation {
    int x, y, z;
};

int main() {
    int tests;
    if (std::scanf("%d", &tests) != 1) return 0;
    while (tests--) {
        int n, m, k;
        if (std::scanf("%d%d%d", &n, &m, &k) != 3) return 1;
        std::vector<Equation> equations(m);
        for (Equation &e : equations) {
            if (std::scanf("%d%d%d", &e.x, &e.y, &e.z) != 3) return 1;
        }
        std::vector<unsigned char> forced(n + 1, 0);
        bool feasible = true;
        long long answer = 0;
        for (int bit = 0; bit < k; ++bit) {
            std::fill(forced.begin(), forced.end(), 0);
            const std::uint32_t mask = std::uint32_t(1) << bit;
            for (const Equation &e : equations) {
                if (static_cast<std::uint32_t>(e.z) & mask) {
                    forced[e.x] = forced[e.y] = 1;
                }
            }
            for (const Equation &e : equations) {
                if (!(static_cast<std::uint32_t>(e.z) & mask)
                    && forced[e.x] && forced[e.y]) {
                    feasible = false;
                    break;
                }
            }
            if (!feasible) break;
            long long count = 0;
            for (int i = 1; i <= n; ++i) count += forced[i];
            answer += count * mask;
        }
        std::printf("%lld\n", feasible ? answer : -1LL);
    }
    return 0;
}
