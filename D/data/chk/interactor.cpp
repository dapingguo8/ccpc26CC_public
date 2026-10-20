// testlib 交互器（interactor）—— 题目「平均」(average)
//
// 依赖：testlib.h（与本文件同目录；评测机若自带 testlib 亦可）。
//   本仓库内附的一份来自 https://github.com/MikeMirzayanov/testlib ；
//   若评测机提供自己的 testlib.h，可直接用评测机的那份覆盖本目录的文件。
//
// 编译：g++ -O2 -std=c++17 -o chk chk.cpp
// 运行：./chk <input-file> <output-file> [<answer-file> [<result-file> [-appes]]]
//   inf     测试数据（只有交互器能看到）：
//             第 1 行 a b c ；第 2 行 q ；随后 q 行每行一个 t
//   stdout  交互器 -> 选手（选手的 stdin 接在这里；每次输出后必须 flush）
//   ouf     选手 -> 交互器（交互器的 stdin 接在选手 stdout 上）
//   tout    argv[2]，交互过程记录（只作日志，评测机可用于事后检查；不接选手）
//   ans     argv[3]，可选；本题不需要（交互器自己重算一切）
//
// 协议（详见 statement/zh-cn.md）：
//   setup：一行 a b c，再一行 q
//   每次询问 t：选手输出 -1 / 0 / k，k>0 时随后 k 轮每轮输出 "x y"（中点为当前值），
//               交互器回一个 x 或 y（二选一），直至到达 S_0 中的值；
//               最后一轮（x,y 都已落在 S_0）交互器不再回数。
//
// 判定：quitf(_ok, ...) 表示 AC；quitf(_wa, ...) 表示答案错误；
//       格式错误（少输出、越界数字）由 testlib 的 ouf.readLong 直接判 _pe。
//
// 关于「二选一」的随机性：本题交互器不是自适应的，但允许在每一轮把两个子节点
// 之一交还给选手（两个子节点都是合法的下一步）。这里用 testlib 的 rnd 并把种子
// 固定为由 (a,b,c,q) 导出的值，使同一组数据的交互过程完全可复现。
//
// 若评测机把 argv[2] 直接接到选手 stdin（少数评测机的约定），把下面的
// SEND_VIA_TOUT 定义打开即可：所有发给选手的内容改写到 tout。
// 不定义时程序会在运行期自动判断：argv[2] 是普通文件（testlib 日志约定）就写
// stdout；argv[2] 是管道/FIFO/字符设备（说明它被接到选手）就改写 tout。
#include "testlib.h"

#include <bits/stdc++.h>
#ifdef _WIN32
#include <windows.h>
#else
#include <sys/stat.h>
#endif
using namespace std;
using i128 = __int128_t;
using u128 = __uint128_t;

// #define SEND_VIA_TOUT   // 见文件头说明

static const long long MAXV = 1LL << 30;   // a,b,c,t <= 2^30
static const int MAXQ = 1000;              // 询问次数上限
static const long long MAXK = 100;         // 答案上界（实际 <= 60）

static bool g_sendViaTout = false;         // 是否把发给选手的内容写进 tout

// 运行期判断 argv[2] 到底是不是"接到选手"的那一端
static void detectOutputTarget(const char *path) {
#ifdef SEND_VIA_TOUT
    g_sendViaTout = true;
    (void)path;
#else
#ifdef _WIN32
    HANDLE h = CreateFileA(path, GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE,
                           NULL, OPEN_EXISTING, 0, NULL);
    if (h != INVALID_HANDLE_VALUE) {
        g_sendViaTout = (GetFileType(h) == FILE_TYPE_PIPE);
        CloseHandle(h);
    }
#else
    struct stat st;
    if (path && stat(path, &st) == 0)
        g_sendViaTout = !S_ISREG(st.st_mode);   // FIFO / 字符设备 / socket
#endif
#endif
}

// 交互器 -> 选手（是普通日志文件时，同时把交互过程记到 tout 里备查）
static void say(const char *fmt, ...) {
    char buf[256];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    if (g_sendViaTout) {
        tout << buf << '\n';
        tout.flush();
    } else {
        fputs(buf, stdout);
        fputc('\n', stdout);
        fflush(stdout);
        tout << buf << '\n';
        tout.flush();
    }
}

static u128 pow2mod(long long e, long long md) {
    // 2^e mod md
    u128 r = 1 % (u128)md, b = 2 % (u128)md;
    while (e > 0) {
        if (e & 1) r = r * b % (u128)md;
        b = b * b % (u128)md;
        e >>= 1;
    }
    return r;
}

// 2^e mod q 预处理（e <= MAXK）：原来每次 valid() 都要跑一遍快速幂，
// 1000 次询问 × 80 层 × 每次两个子节点，光这一项就要 1s 上下。
static u128 POW2[MAXK + 1];

static void preparePow2(long long md) {
    POW2[0] = 1 % (u128)md;
    for (int e = 1; e <= MAXK; e++) POW2[e] = POW2[e - 1] * 2 % (u128)md;
}

struct Solver {
    long long a, b, c;
    long long d, u, g, p, q;
    long long inv;      // p^{-1} mod q
    u128 q2u;           // q * 2^u，delta 的上界

    void init(long long a_, long long b_, long long c_) {
        a = a_; b = b_; c = c_;
        long long ba = b - a, ca = c - a;
        d = __gcd(ba, ca);
        long long tmp = d;
        u = 0;
        while (tmp % 2 == 0) { tmp /= 2; u++; }
        g = tmp;
        p = ba / d;
        q = ca / d;
        inv = modinv(p, q);
        q2u = (u128)q << u;
    }

    static long long modinv(long long x, long long mod) {
        long long r0 = x, r1 = mod;
        i128 s0 = 1, s1 = 0;
        while (r1) {
            long long quot = r0 / r1;
            long long t = r0 - quot * r1; r0 = r1; r1 = t;
            i128 s = s0 - (i128)quot * s1; s0 = s1; s1 = s;
        }
        long long res = (long long)(s0 % mod);
        if (res < 0) res += mod;
        return res;
    }

    // delta >= 0 在深度 r 可达？即 a + g*delta 属于 S_r
    bool valid(i128 delta, int r) {
        if (delta < 0) return false;
        if ((u128)delta > q2u) return false;
        int e = r - (int)u;
        if (e >= 0) {
            u128 twoE = (u128)1 << e;
            u128 dm = (u128)delta % (u128)q;
            u128 r0 = dm * POW2[e] % (u128)q;
            r0 = r0 * (u128)inv % (u128)q;
            u128 rp = r0 * (u128)p;
            u128 need = (rp + twoE - 1) / twoE;
            if ((u128)delta < need) return false;
            u128 rqp = r0 * (u128)(q - p);
            u128 D = q2u - (u128)delta;
            u128 need2 = (rqp + twoE - 1) / twoE;
            if (need2 > D) return false;
            return true;
        } else {
            int sh = -e;
            long long mod = 1LL << sh;
            if ((long long)delta % mod != 0) return false;
            i128 m = (i128)delta >> sh;
            u128 r0 = (u128)m % (u128)q * (u128)inv % (u128)q;
            u128 rp = r0 * (u128)p;
            if ((u128)m < rp) return false;
            u128 sm = r0 + ((u128)m - rp) / (u128)q;
            return sm <= ((u128)1 << r);
        }
    }

    int min_k(i128 delta) {
        for (int k = 0; k <= MAXK; k++)
            if (valid(delta, k)) return k;
        return -1;
    }
};

int main(int argc, char *argv[]) {
    if (argc >= 3)
        detectOutputTarget(argv[2]);
    registerInteraction(argc, argv);

    // ---------------- 读入测试数据（只有交互器能看到） ----------------
    long long a = inf.readLong(0, MAXV, "a");
    long long b = inf.readLong(0, MAXV, "b");
    long long c = inf.readLong(0, MAXV, "c");
    if (!(a < b && b < c))
        quitf(_fail, "input error: expected 0 <= a < b < c <= 2^30, got %lld %lld %lld", a, b, c);

    long long qn = inf.readLong(1LL, (long long)MAXQ, "q");
    vector<long long> ts(qn);
    for (long long i = 0; i < qn; i++)
        ts[i] = inf.readLong(0, MAXV, format("t[%lld]", i + 1));
    if (!inf.seekEof())
        quitf(_fail, "input error: extra data after %lld queries", qn);

    Solver sol;
    sol.init(a, b, c);
    preparePow2(sol.q);

    // 固定的随机种子：同一组数据的交互过程可复现
    rnd.setSeed(a * 1000003LL + b * 1000033LL + c + qn);

    // ---------------- 交互 ----------------
    say("%lld %lld %lld", a, b, c);
    say("%lld", qn);

    for (long long qi = 0; qi < qn; qi++) {
        long long t = ts[qi];
        say("%lld", t);

        int kexp = -1;
        if (t >= a && t <= c && (t - a) % sol.g == 0) {
            i128 delta = (t - a) / sol.g;
            kexp = sol.min_k(delta);
        }

        long long k = ouf.readLong(-1, MAXK, "k");
        if (kexp == -1) {
            if (k != -1)
                quitf(_wa, "query %lld: t = %lld is unreachable, expected -1, found %lld",
                      qi + 1, t, k);
            continue;
        }
        if (k != kexp)
            quitf(_wa, "query %lld: wrong k, found %lld, expected %d", qi + 1, k, kexp);
        if (k == 0) {
            if (t != a && t != b && t != c)
                quitf(_wa, "query %lld: k = 0 but t = %lld is not in S_0", qi + 1, t);
            continue;
        }

        // k > 0：k 轮
        long long cur = t;
        for (long long r = k; r >= 1; r--) {
            long long x = ouf.readLong(0, MAXV, "x");
            long long y = ouf.readLong(0, MAXV, "y");
            if (x + y != 2 * cur)
                quitf(_wa, "query %lld round %lld: %lld + %lld != 2 * %lld",
                      qi + 1, k - r + 1, x, y, cur);
            for (long long w : {x, y}) {
                if (w < a || w > c || (w - a) % sol.g != 0)
                    quitf(_wa, "query %lld round %lld: child %lld out of range [%lld, %lld] or "
                               "not congruent to a modulo g = %lld",
                          qi + 1, k - r + 1, w, a, c, sol.g);
                i128 delta = (w - a) / sol.g;
                if (!sol.valid(delta, (int)r - 1))
                    quitf(_wa, "query %lld round %lld: child %lld is not in S_%lld",
                          qi + 1, k - r + 1, w, r - 1);
            }
            if (r == 1) break;                 // 最后一轮：u,v 已在 S_0，交互器不再回数
            long long choice = rnd.next(2) ? y : x;   // 两个子节点都合法，任选一个还给选手
            say("%lld", choice);
            cur = choice;
        }
    }

    quitf(_ok, "%lld quer%s answered correctly", qn, qn == 1 ? "y" : "ies");
}
