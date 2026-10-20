#include <cstdint>
#include <cstdio>
#include <vector>

class FastInput {
    static const std::size_t SIZE = 1 << 16;
    unsigned char buffer[SIZE];
    std::size_t position = 0, length = 0;

    int next() {
        if (position == length) {
            length = std::fread(buffer, 1, SIZE, stdin);
            position = 0;
            if (length == 0) return EOF;
        }
        return buffer[position++];
    }

public:
    bool read(std::uint32_t &value) {
        int c;
        do {
            c = next();
            if (c == EOF) return false;
        } while (c <= ' ');
        value = 0;
        while (c >= '0' && c <= '9') {
            value = value * 10 + static_cast<std::uint32_t>(c - '0');
            c = next();
        }
        return true;
    }
};

struct Constraint {
    std::uint32_t x, y, z;
};

int main() {
    FastInput input;
    std::uint32_t tests;
    if (!input.read(tests)) return 0;
    while (tests--) {
        std::uint32_t n, m, k;
        if (!input.read(n) || !input.read(m) || !input.read(k)) return 1;
        std::vector<std::uint32_t> candidate(n + 1, 0);
        std::vector<Constraint> constraints(m);
        for (Constraint &e : constraints) {
            if (!input.read(e.x) || !input.read(e.y) || !input.read(e.z)) return 1;
            candidate[e.x] |= e.z;
            candidate[e.y] |= e.z;
        }
        bool feasible = true;
        for (const Constraint &e : constraints) {
            if ((candidate[e.x] & candidate[e.y]) != e.z) {
                feasible = false;
                break;
            }
        }
        if (!feasible) {
            std::puts("-1");
            continue;
        }
        long long answer = 0;
        for (std::uint32_t i = 1; i <= n; ++i) answer += candidate[i];
        std::printf("%lld\n", answer);
    }
    return 0;
}
