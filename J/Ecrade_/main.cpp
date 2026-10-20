#include <cstdint>
#include <cstdio>
#include <vector>

struct Equation {
    std::uint32_t x, y, z;
};

class FastInput {
    static const int buffer_size = 1 << 16;
    char buffer[buffer_size];
    int position = 0, length = 0;

    int get_char() {
        if (position == length) {
            length = static_cast<int>(std::fread(buffer, 1, buffer_size, stdin));
            position = 0;
            if (length == 0) return EOF;
        }
        return buffer[position++];
    }

public:
    bool read(std::uint32_t &value) {
        int ch;
        do {
            ch = get_char();
            if (ch == EOF) return false;
        } while (ch <= ' ');
        value = 0;
        while ('0' <= ch && ch <= '9') {
            value = value * 10 + static_cast<std::uint32_t>(ch - '0');
            ch = get_char();
        }
        return true;
    }
};

int main() {
    FastInput input;
    std::uint32_t tests;
    if (!input.read(tests)) return 0;

    while (tests--) {
        std::uint32_t n, m, k;
        if (!input.read(n) || !input.read(m) || !input.read(k)) return 1;

        std::vector<Equation> equations(m);
        std::vector<std::uint32_t> minimum(n + 1, 0);
        for (Equation &equation : equations) {
            if (!input.read(equation.x) || !input.read(equation.y)
                || !input.read(equation.z)) return 1;
            minimum[equation.x] |= equation.z;
            minimum[equation.y] |= equation.z;
        }

        bool feasible = true;
        for (const Equation &equation : equations) {
            if ((minimum[equation.x] & minimum[equation.y]) != equation.z) {
                feasible = false;
                break;
            }
        }

        if (!feasible) {
            std::puts("-1");
            continue;
        }
        long long answer = 0;
        for (std::uint32_t i = 1; i <= n; ++i) answer += minimum[i];
        std::printf("%lld\n", answer);
    }
    return 0;
}
