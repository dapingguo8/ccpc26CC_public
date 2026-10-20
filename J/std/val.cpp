#include <cctype>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string>

[[noreturn]] void fail(const std::string &message) {
    std::fprintf(stderr, "Invalid input: %s\n", message.c_str());
    std::exit(1);
}

class ValidatorInput {
    static const std::size_t SIZE = 1 << 16;
    FILE *file;
    unsigned char buffer[SIZE];
    std::size_t position = 0, length = 0;
    std::uint64_t token = 0;

    int next() {
        if (position == length) {
            length = std::fread(buffer, 1, SIZE, file);
            position = 0;
            if (length == 0) {
                if (std::ferror(file)) fail("cannot read input");
                return EOF;
            }
        }
        return buffer[position++];
    }

    static bool space(int c) {
        return c != EOF && std::isspace(static_cast<unsigned char>(c));
    }

public:
    explicit ValidatorInput(FILE *source) : file(source) {}

    std::uint64_t read(const std::string &name, std::uint64_t low,
                       std::uint64_t high) {
        int c;
        do {
            c = next();
        } while (space(c));
        ++token;
        const std::string context = "token " + std::to_string(token)
            + " (" + name + ")";
        if (c == EOF) fail("unexpected EOF at " + context);
        std::uint64_t value = 0;
        while (c != EOF && !space(c)) {
            if (c < '0' || c > '9') {
                fail(context + " must be an unsigned decimal integer");
            }
            const std::uint64_t digit = static_cast<std::uint64_t>(c - '0');
            if (value > high / 10
                || (value == high / 10 && digit > high % 10)) {
                fail(context + " exceeds " + std::to_string(high));
            }
            value = value * 10 + digit;
            c = next();
        }
        if (value < low) {
            fail(context + " is below " + std::to_string(low));
        }
        return value;
    }

    void expectEOF() {
        int c;
        do {
            c = next();
        } while (space(c));
        if (c != EOF) fail("extra data after the final test case");
    }
};

int main(int argc, char **argv) {
    if (argc > 2) {
        std::fprintf(stderr, "Usage: %s [input-file]\n", argv[0]);
        return 1;
    }
    FILE *source = stdin;
    if (argc == 2) {
        source = std::fopen(argv[1], "rb");
        if (!source) {
            std::fprintf(stderr, "Cannot open input file: %s\n", argv[1]);
            return 1;
        }
    }
    ValidatorInput input(source);
    // T has no independent upper limit: n >= 1 and sum_n <= 500000
    // imply T <= 500000. Include that aggregate reason in T diagnostics.
    const std::uint64_t tests = input.read(
        "T, derived from sum_n <= 500000 since n >= 1", 1, 500000);
    std::uint64_t sum_n = 0, sum_m = 0;
    for (std::uint64_t test = 1; test <= tests; ++test) {
        const std::string context = "test " + std::to_string(test) + ", ";
        const std::uint64_t n = input.read(context + "n", 1, 200000);
        const std::uint64_t m = input.read(context + "m", 0, 200000);
        const std::uint64_t k = input.read(context + "k", 1, 30);
        sum_n += n;
        sum_m += m;
        if (sum_n > 500000) {
            fail(context + "sum_n exceeds 500000 (" + std::to_string(sum_n) + ")");
        }
        if (sum_m > 500000) {
            fail(context + "sum_m exceeds 500000 (" + std::to_string(sum_m) + ")");
        }
        const std::uint64_t maxValue = (std::uint64_t(1) << k) - 1;
        for (std::uint64_t i = 1; i <= m; ++i) {
            const std::string equation = context + "equation "
                + std::to_string(i) + ", ";
            input.read(equation + "x", 1, n);
            input.read(equation + "y", 1, n);
            input.read(equation + "z", 0, maxValue);
        }
    }
    input.expectEOF();
    if (source != stdin) std::fclose(source);
    std::fprintf(stderr, "Valid input: %llu test case(s)\n",
                 static_cast<unsigned long long>(tests));
    return 0;
}
