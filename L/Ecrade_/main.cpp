#include <algorithm>
#include <cstdio>
#include <string>

int main() {
    int tests;
    if (std::scanf("%d", &tests) != 1) return 0;
    while (tests--) {
        char buffer[1000005];
        if (std::scanf("%1000004s", buffer) != 1) return 1;
        const std::string s(buffer);
        int total = 0, largest = 0, first = 0, last = 0, groups = 0;
        for (int i = 0, n = static_cast<int>(s.size()); i < n; ++i) {
            if (s[i] != '1') continue;
            int width = 1;
            while (i + 2 < n && s[i + 1] == '0' && s[i + 2] == '1') {
                i += 2;
                ++width;
            }
            if (groups++ == 0) first = width;
            last = width;
            total += width;
            if (width > largest) largest = width;
        }
        if (groups == 0) {
            std::puts("1");
            continue;
        }
        if (groups == 1) {
            int answer = 2 * first - 1;
            answer += s.front() == '0';
            answer += s.back() == '0';
            std::printf("%d\n", answer);
            continue;
        }
        const int remaining = std::max(total & 1, 2 * largest - total);
        if (remaining == 0) {
            std::puts("1");
            continue;
        }
        const bool left = s.front() == '1'
            && (2 * largest < total || first == largest);
        const bool right = s.back() == '1'
            && (2 * largest < total || last == largest);
        std::printf("%d\n", 2 * remaining + (left || right ? 0 : 1));
    }
    return 0;
}
