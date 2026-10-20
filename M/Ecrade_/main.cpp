#include <algorithm>
#include <cstdio>
#include <vector>

int gcd_value(int a, int b) {
    while (b != 0) {
        const int next = a % b;
        a = b;
        b = next;
    }
    return a;
}

int main() {
    int n, limit;
    if (std::scanf("%d%d", &n, &limit) != 2) return 0;
    std::vector<int> values(n);
    for (int &value : values) std::scanf("%d", &value);

    std::vector<int> divisors(limit + 1, 0);
    for (int d = 2; d <= limit; ++d)
        for (int x = d; x <= limit; x += d) ++divisors[x];

    long long answer = 0;
    for (int sum = 0; sum <= 2 * n; ++sum) {
        int left = std::max(0, sum - n + 1);
        int right = sum / 2;
        int current = 0;
        for (int i = right; i >= left; --i) {
            const int j = sum - i;
            if (i == j) continue;
            current = gcd_value(current, std::abs(values[i] - values[j]));
            answer += current == 0 ? limit - 1 : divisors[current];
            if (current == 1) break;
        }
    }
    std::printf("%lld\n", answer);
    return 0;
}
