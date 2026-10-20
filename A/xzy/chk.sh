#!/usr/bin/env bash
set -u
shopt -s nullglob

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"
DATA_ROOT="../data"
if [[ -d "$DATA_ROOT/2dmatrix" ]]; then
    DATA_DIR="$DATA_ROOT/2dmatrix"
else
    DATA_DIR="$DATA_ROOT"
fi
CXX=${CXX:-g++}
TMP=$(mktemp -d "${TMPDIR:-/tmp}/ccpc-matrix-chk.XXXXXX")
trap 'rm -rf "$TMP"' EXIT

if ! "$CXX" -std=c++14 -O2 -pipe std.cpp -o std; then
    echo "failed to compile std.cpp in the current directory" >&2
    exit 1
fi
if ! "$CXX" -std=c++14 -O2 -pipe BF.cpp -o BF; then
    echo "failed to compile BF.cpp in the current directory" >&2
    exit 1
fi

status=0
checked=0

compare_output() {
    local solver=$1
    local label=$2
    local input=$3
    local answer=$4
    local output="$TMP/output"
    if ! "./$solver" < "$input" > "$output"; then
        echo "RUNTIME $label" >&2
        status=1
    elif diff -u <(tr -d '\r' < "$output") <(tr -d '\r' < "$answer") >/dev/null; then
        echo "accepted $label"
    else
        echo "WRONG    $label" >&2
        diff -u <(tr -d '\r' < "$output") <(tr -d '\r' < "$answer") || true
        status=1
    fi
    checked=$((checked + 1))
}

for input in "$DATA_DIR"/*.in; do
    [[ "$(basename "$input")" =~ ^[0-9]+\.in$ ]] || continue
    answer="${input%.in}.ans"
    compare_output std "std $(basename "$input")" "$input" "$answer"
done

for number in 1 23; do
    if [[ -f "$DATA_DIR/$number.in" && -f "$DATA_DIR/$number.ans" ]]; then
        compare_output BF "BF $number.in" "$DATA_DIR/$number.in" "$DATA_DIR/$number.ans"
    fi
done

if (( checked == 0 )); then
    echo "no numeric .in files found under $DATA_DIR" >&2
    status=1
fi
echo "2dmatrix checker compared $checked runs"

rm std
rm BF

exit "$status"
