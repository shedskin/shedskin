#!/usr/bin/env bash
# DEBUG: run the already built test_prog_spelling (tests/build) many times, under a few
# variants, and show what we can for each failure: stderr (with SHEDSKIN_GC_DEBUG set, the
# allocation/free history of the bad pointer plus a backtrace), the backtrace resolved with
# addr2line, and gdb's backtrace from the core dump, if core dumps are enabled.
#
# usage: .github/debug_spelling.sh [runs]
#   PYTHON:   python executable (default: .venv/bin/python, else python3)
#   CORE_DIR: where kernel.core_pattern puts core dumps (default: /tmp/cores)

set -u
RUNS=${1:-100}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
DIR=$ROOT/tests/build/test_prog_spelling
PY=${PYTHON:-$ROOT/.venv/bin/python}
[ -x "$PY" ] || PY=$(command -v python3)
PY=$(readlink -f "$PY")
CORE_DIR=$(readlink -f "${CORE_DIR:-/tmp/cores}")
SHOW=3  # failures to show in detail, per variant

cd "$DIR" || exit 1
ulimit -c unlimited 2>/dev/null
echo "python: $PY ($("$PY" --version 2>&1)), runs per variant: $RUNS, cpus: $(nproc)"
echo "core pattern: $(cat /proc/sys/kernel/core_pattern 2>/dev/null)"
echo "kernel: $(uname -a)"
echo "cpu: $(grep -m1 'model name' /proc/cpuinfo)"
echo "aslr: $(cat /proc/sys/kernel/randomize_va_space 2>/dev/null), thp: $(cat /sys/kernel/mm/transparent_hugepage/enabled 2>/dev/null)"
echo "stack limit: $(ulimit -s)"
echo "--- ldd test_prog_spelling.so ---"
ldd test_prog_spelling.so
echo "--- exported GC_ symbols (should be none) ---"
nm -D --defined-only test_prog_spelling.so | grep ' GC_' | head

summary=""
failed=0

run_variant() {  # binary (for gdb) / name / command..
    local binary=$1 name=$2
    shift 2
    local fails=0 shown=0 status i core
    echo
    echo "=== $name ==="
    for i in $(seq "$RUNS"); do
        rm -f "$CORE_DIR"/core* 2>/dev/null
        "$@" >out.txt 2>err.txt
        status=$?
        [ $status -eq 0 ] && continue
        fails=$((fails+1))
        [ $shown -ge $SHOW ] && continue
        shown=$((shown+1))
        echo "--- $name: run $i failed (exit status $status) ---"
        tail -n 100 err.txt
        if grep -q 'test_prog_spelling\.so(+0x' err.txt; then
            echo "--- backtrace, resolved ---"
            grep -o 'test_prog_spelling\.so(+0x[0-9a-f]*)' err.txt | sed 's/.*(+\(0x[0-9a-f]*\))/\1/' |
                xargs addr2line -f -C -i -p -e test_prog_spelling.so
        fi
        core=$(ls -t "$CORE_DIR"/core* 2>/dev/null | head -n 1)
        if [ -n "$core" ] && command -v gdb >/dev/null; then
            echo "--- gdb: $core ---"
            gdb -q -batch -ex "bt 60" -ex "bt full 20" "$binary" "$core" 2>&1 | grep -v '^\[New LWP' | head -n 400
        fi
    done
    echo "=== $name: $fails/$RUNS failed ==="
    summary="$summary$(printf '%-55s %4d/%d' "$name" "$fails" "$RUNS")"$'\n'
    [ $fails -eq 0 ] || failed=1
}

EXT=(-c "from test_prog_spelling import test_all; test_all()")

run_variant "$PY" "ext, SHEDSKIN_GC_DEBUG=1" env SHEDSKIN_GC_DEBUG=1 "$PY" "${EXT[@]}"
run_variant "$PY" "ext, as run by ctest" "$PY" "${EXT[@]}"
run_variant "$PY" "ext, GC_MARKERS=1 (no parallel marking)" env GC_MARKERS=1 SHEDSKIN_GC_DEBUG=1 "$PY" "${EXT[@]}"
run_variant "$PY" "ext, no ASLR" setarch "$(uname -m)" -R env SHEDSKIN_GC_DEBUG=1 "$PY" "${EXT[@]}"
run_variant "$PY" "ext, GC_DONT_GC=1 (no collections)" env GC_DONT_GC=1 SHEDSKIN_GC_DEBUG=1 "$PY" "${EXT[@]}"
run_variant "$PY" "ext, GC_FREE_SPACE_DIVISOR=300 (~25x more collections)" env GC_FREE_SPACE_DIVISOR=300 SHEDSKIN_GC_MIN_BYTES=1 SHEDSKIN_GC_DEBUG=1 "$PY" "${EXT[@]}"
run_variant ./test_prog_spelling "exe, SHEDSKIN_GC_DEBUG=1" env SHEDSKIN_GC_DEBUG=1 ./test_prog_spelling

echo
echo "=== summary ==="
printf '%s' "$summary"
exit $failed
