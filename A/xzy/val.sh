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

if ! "$CXX" -std=c++14 -O2 -pipe val.cpp -o val; then
    echo "failed to compile val.cpp in the current directory" >&2
    exit 1
fi

status=0
checked=0

for input in "$DATA_DIR"/*.in; do
    [[ "$(basename "$input")" =~ ^[0-9]+\.in$ ]] || continue
    if ./val < "$input"; then
        echo "valid   $(basename "$input")"
    else
        echo "INVALID $(basename "$input")" >&2
        status=1
    fi
    checked=$((checked + 1))
done

if (( checked == 0 )); then
    echo "no numeric .in files found under $DATA_DIR" >&2
    status=1
fi
echo "2dmatrix validator checked $checked files"

rm val

exit "$status"
