#!/usr/bin/env python3

"""
Local testing tool for Triplet

Disclaimer: This is NOT the same code used to test your solution when it is submitted.
This tool is provided as-is. Its purpose is to help with debugging the interactive
problem and it has no ambitions to extensively test all possibilities that
are allowed by the problem statement. While the tool tries to yield the same
results as the real judging system, this is not guaranteed and the result
may differ if the tested program does not use the correct formatting or
exhibits other incorrect behavior. The tool also *does not* enforce time and
memory limits that are applied to submitted solutions.

Feel free to make whatever alterations or augmentations you like.

The behavior is controlled by an input data file.
The first line of the file contains two integers: T (number of testcases) and seed.
For each testcase:
-   The first line contains an integer n, the length of the target string.
-   The second line contains a binary string s of length n, representing the target string.
 
Assigning seed to 0 will disable shuffling of testcases.

Here is an example file:    
3 20261018
1
0
3
111
6
001100

The testing tool is run like this on Windows:
    python triplet_testing_tool.py <data_file> <program> <arguments>
or on Linux:
    python3 triplet_testing_tool.py <data_file> <program> <arguments>

where `arguments` are optional arguments to the program to run. The following
show examples for different languages:

    python3 triplet_testing_tool.py 1.in ./myprogram
    python3 triplet_testing_tool.py 1.in java -cp . MyProgram
    python3 triplet_testing_tool.py 1.in python3 myprogram.py

The tool logs the complete interaction.
If you do not want that, pass `--quiet` (before the data file name).
"""

from __future__ import annotations

import argparse
import random
import subprocess
import sys
from typing import List, Tuple


verbose = True
process = None
run_id = 0


class WrongAnswer(RuntimeError):
    pass


class EndOfFile(RuntimeError):
    pass


def vprint(*args, **kwargs) -> None:
    if verbose:
        print("> ", end="")
        print(*args, **kwargs)
        sys.stdout.flush()
    print(*args, file=process.stdin, flush=True, **kwargs)


def vreadline(optional: bool = False) -> str:
    line = process.stdout.readline()
    if verbose and line:
        print("<", line.rstrip("\n"))
    if not line and not optional:
        raise EndOfFile("The program stopped producing output.")
    return line

def read_case(path: str) -> Tuple[int, List[Tuple[int, str]], int]:
    """Read the input data file.

    The first line holds two integers, T and seed (seed may be omitted, which
    is the same as seed = 0). Every testcase then consists of two lines: the
    positive integer n and a binary string s of length n.
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        raise ValueError("Input file is empty.")

    header = lines[0].split()
    if len(header) > 2:
        raise ValueError(f"First line {lines[0]!r} must contain T and seed.")
    try:
        T = int(header[0])
        seed = int(header[1]) if len(header) > 1 else 0
    except ValueError:
        raise ValueError(f"First line {lines[0]!r} must contain T and seed.")
    if T < 0:
        raise ValueError(f"T = {T} is negative.")

    tests: List[Tuple[int, str]] = []
    pos = 1
    for i in range(T):
        if pos + 2 > len(lines):
            raise ValueError(f"Input file is too short, test case {i + 1} is incomplete.")
        n = int(lines[pos])
        s = lines[pos + 1]
        pos += 2

        if n < 1:
            raise ValueError(f"Test case {i + 1}: n = {n} is not a positive integer.")
        if set(s) - set("01"):
            raise ValueError(f"Test case {i + 1}: {s!r} is not a binary string.")
        if len(s) != n:
            raise ValueError(
                f"Test case {i + 1}: {s!r} has length {len(s)}, expected {n}."
            )
        tests.append((n, s))

    if pos != len(lines):
        raise ValueError(f"Input file has {len(lines) - pos} unexpected trailing line(s).")

    return T, tests, seed


def start_process(program: List[str], phase: str, bufsize: int | None = None) -> subprocess.Popen:
    global run_id, process
    run_id += 1
    if verbose:
        print(f"[run {run_id}] {phase}: {' '.join(program)}")
    kwargs = {
        "shell": True,
        "stdin": subprocess.PIPE,
        "stdout": subprocess.PIPE,
        "text": True,
    }
    if bufsize is not None:
        kwargs["bufsize"] = bufsize
    process = subprocess.Popen(" ".join(program), **kwargs)
    if process.stdin is None or process.stdout is None:
        raise RuntimeError("Failed to open pipes.")
    return process

def vread_int(case_id: int) -> int:
    """Read one line that must contain a single integer."""
    line = vreadline().strip()
    try:
        return int(line)
    except ValueError:
        raise WrongAnswer(f"Case {case_id}: expected an integer, got {line!r}.")


def check_answer(n: int, s: str, case_id: int, raw_n: int) -> None:
    """Check the answer of one testcase of the first run."""
    if n < 1:
        raise WrongAnswer(f"Case {case_id}: n = {n} is not a positive integer.")
    if set(s) - set("01"):
        raise WrongAnswer(f"Case {case_id}: {s!r} is not a binary string.")
    if len(s) != n:
        raise WrongAnswer(f"Case {case_id}: {s!r} has length {len(s)}, expected {n}.")
    if "000" in s or "111" in s:
        raise WrongAnswer(
            f"Case {case_id}: {s!r} contains three consecutive equal characters."
        )
    if n * 2 > 3 * raw_n:
        raise WrongAnswer(
            f"Case {case_id}: n' = {n} > 1.5n = 1.5 * {raw_n} = {1.5 * raw_n}."
        )  

def run_encode(
    program: List[str], T: int, tests: List[Tuple[int, str]]
) -> List[Tuple[int, str]]:
    """First run: hand the input data to the program and collect its answers."""
    start_process(program, "First run", bufsize=1)
    vprint(str(T) + " 1")

    answers: List[Tuple[int, str]] = []
    for case_id, (n, s) in enumerate(tests, start=1):
        if verbose:
            print(f"Case {case_id}: n = {n}, s = {s}")
        vprint(str(n))
        vprint(s)
        n_ans = vread_int(case_id)
        s_ans = vreadline().strip()
        check_answer(n_ans, s_ans, case_id, n)
        answers.append((n_ans, s_ans))

    if process.stdin:
        process.stdin.close()
    process.wait()
    if process.returncode != 0:
        raise WrongAnswer(f"First run exit code {process.returncode}.")
    return answers


def run_decode(
    program: List[str],
    T: int,
    answers: List[Tuple[int, str]],
    tests: List[Tuple[int, str]],
    seed: int,
) -> None:
    """Second run: hand the shuffled answers back and check the round trip."""
    start_process(program, "Second run", bufsize=1)

    vprint(str(T) + " 2")

    order = list(zip(answers, tests))
    if seed:
        random.Random(seed).shuffle(order)

    for case_id, ((n_ans, s_ans), (n, s)) in enumerate(order, start=1):
        if verbose:
            print(f"Case {case_id}: n = {n_ans}, s = {s_ans}")
        vprint(str(n_ans))
        vprint(s_ans)
        n_back = vread_int(case_id)
        s_back = vreadline().strip()
        if set(s_back) - set("01"):
            raise WrongAnswer(f"Case {case_id}: {s_back!r} is not a binary string.")
        if len(s_back) != n_back:
            raise WrongAnswer(
                f"Case {case_id}: {s_back!r} has length {len(s_back)}, expected {n_back}."
            )
        if (n_back, s_back) != (n, s):
            raise WrongAnswer(
                f"Case {case_id}: expected {n} and {s}, got {n_back} and {s_back}."
            )
    try:
        process.stdin.close()
    except Exception:
        pass
    process.wait(timeout=5)
    if process.returncode != 0:
        raise WrongAnswer(f"Second run exit code {process.returncode}.")



def main() -> int:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [--quiet] data.in program [args...]"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Do not show interactions"
    )
    parser.add_argument("data", help="Input file that controls the behavior of the tool")
    parser.add_argument("program", nargs=argparse.REMAINDER, help="Program to run")
    args = parser.parse_args()

    global verbose
    verbose = not args.quiet

    if not args.program:
        parser.error("Must specify program to run")

    T, tests, seed = read_case(args.data)

    answers = run_encode(args.program, T, tests)
    run_decode(args.program, T, answers, tests, seed)

    print(f"Program finished correctly.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (WrongAnswer, EndOfFile) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
