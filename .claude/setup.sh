#!/usr/bin/env bash
# Prepare a machine for translating and compiling shedskin output.
#
# Idempotent and safe to re-run: every step is skipped when already satisfied.
# Used by the SessionStart hook in .claude/settings.json, and callable by hand.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Boehm GC and PCRE are what the generated C++ links against. Building them from
# the bundled ext/ sources takes minutes; the distro packages take seconds.
missing=()
[ -f /usr/include/gc/gc_allocator.h ] || missing+=(libgc-dev)
[ -f /usr/include/pcre.h ] || missing+=(libpcre3-dev)
if [ ${#missing[@]} -gt 0 ]; then
    if command -v apt-get >/dev/null 2>&1; then
        apt-get install -y "${missing[@]}" >/dev/null 2>&1 \
            || echo "setup.sh: could not install ${missing[*]}; 'shedskin runtests' can build them from ext/ instead" >&2
    elif command -v brew >/dev/null 2>&1; then
        brew install bdw-gc pcre >/dev/null 2>&1 || true
    fi
fi

# Check for installed package metadata, not 'import shedskin': run from the repo
# root, the import finds the source tree even when nothing is installed.
python3 -c 'import importlib.metadata as m; m.version("shedskin")' 2>/dev/null \
    || pip install -q -e "$repo_root"

echo "setup.sh: ready (shedskin $(python3 -c 'import importlib.metadata as m; print(m.version("shedskin"))'))"
