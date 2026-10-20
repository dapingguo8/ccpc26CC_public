#!/usr/bin/env bash
set -euo pipefail

# Resolve all paths from this script, regardless of the caller's directory.
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
shopt -s nullglob
inputs=(../data/*.in)
if (( ${#inputs[@]} == 0 )); then
    echo "ERROR: no .in files found in ../data" >&2
    exit 1
fi

# The .exe suffix also works on Linux; bin/ is ignored by the repository.
mkdir -p bin
"${CXX:-g++}" -std=c++14 -O2 -Wall -Wextra validator.cpp -o bin/validator.exe

failed=0
for input in "${inputs[@]}"; do
    if ./bin/validator.exe "$input"; then
        printf 'PASS %s\n' "$input"
    else
        printf 'FAIL %s\n' "$input" >&2
        failed=$((failed + 1))
    fi
done

printf 'Checked %d files: %d passed, %d failed.\n' \
    "${#inputs[@]}" "$((${#inputs[@]} - failed))" "$failed"
exit "$((failed != 0))"
