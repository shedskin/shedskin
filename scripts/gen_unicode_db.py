#!/usr/bin/env python3
"""Generate shedskin/lib/builtin/unicode_db.{hpp,cpp}: the character database behind
the str methods (character classes and full case mappings).

Every property is taken from the running CPython's own str methods, so the
compiled str methods agree with that CPython (and its unicode version) by
construction, including the special cases (multi-character mappings such as
'\\xdf'.upper() == 'SS', XID_Start/XID_Continue for isidentifier, the
Case_Ignorable property used by lower()'s final sigma rule).

Writes unicode_db.hpp (table shapes, included from unicode.hpp) and
unicode_db.cpp (the data, included from unicode.cpp). Usage, from the
repository root and with the CPython whose unicode version the runtime
should follow:

    python3 scripts/gen_unicode_db.py shedskin/lib/builtin
"""

import os

import sys
import unicodedata

MAXCP = 0x110000

# must match unicode.hpp
ALPHA = 0x0001
DECIMAL = 0x0002
DIGIT = 0x0004
NUMERIC = 0x0008
LOWER = 0x0010
UPPER = 0x0020
TITLE = 0x0040
CASED = 0x0080
CASE_IGNORABLE = 0x0100
SPACE = 0x0200
XID_START = 0x0400
XID_CONTINUE = 0x0800
EXTENDED_CASE = 0x1000

SIGMA = 0x3A3


def properties(cp, ext, ext_index):
    c = chr(cp)
    flags = 0
    if c.isalpha():
        flags |= ALPHA
    if c.isdecimal():
        flags |= DECIMAL
    if c.isdigit():
        flags |= DIGIT
    if c.isnumeric():
        flags |= NUMERIC
    if c.islower():
        flags |= LOWER
    if c.isupper():
        flags |= UPPER
    if c.istitle() and not c.isupper():
        flags |= TITLE
    if flags & (LOWER | UPPER | TITLE):
        flags |= CASED
    if c.isspace():
        flags |= SPACE
    if cp != ord('_') and c.isidentifier():
        flags |= XID_START
    if ('a' + c).isidentifier():
        flags |= XID_CONTINUE

    # Case_Ignorable is not exposed directly, but CPython's final sigma rule
    # (see __ss_lower_sigma in unicode.cpp) skips over case-ignorable
    # characters in both directions: a capital sigma preceded by c alone
    # stays a normal sigma if c is skipped (nothing cased before it), while
    # with a cased letter in front of c it becomes final only if c is
    # skipped or c is itself cased.
    if cp != SIGMA:
        alone = (c + '\u03a3').lower()[-1] == '\u03c2'
        after_cased = ('A' + c + '\u03a3').lower()[-1] == '\u03c2'
        if after_cased and not alone:
            flags |= CASE_IGNORABLE

    decimal = int(c) if c.isdecimal() else -1

    maps = [c.upper(), c.lower(), c.title(), c.casefold()]
    if cp == SIGMA:
        maps[1] = '\u03c3'  # context-free part; the rest is in lower()

    if all(len(m) == 1 for m in maps):
        return (flags, decimal) + tuple(ord(m) - cp for m in maps)

    flags |= EXTENDED_CASE
    refs = []
    for m in maps:
        key = tuple(ord(x) for x in m)
        if key not in ext_index:
            ext_index[key] = len(ext)
            ext.extend(key)
        assert len(key) < 4
        refs.append((len(key) << 24) | ext_index[key])
    return (flags, decimal) + tuple(refs)


def dedup_blocks(t, size):
    """split t into blocks of the given size; returns (block ids, unique
    blocks concatenated), so that t[i] == data[(ids[i // size] * size) + i % size]"""
    blocks = {}
    ids = []
    data = []
    for i in range(0, len(t), size):
        block = tuple(t[i:i + size])
        if block not in blocks:
            blocks[block] = len(blocks)
            data.extend(block)
        ids.append(blocks[block])
    return ids, data


def split_bins(t):
    """three-level table (like CPython's makeunicodedata.py uses two):

        t[i] == t3[(t2[(t1[i >> shift1] << (shift1 - shift2)) +
                       ((i >> shift2) & mask12)] << shift2) + (i & mask2)]

    returns the smallest (in bytes) split found."""
    best = None
    for shift2 in range(2, 8):
        mid, t3 = dedup_blocks(t, 1 << shift2)
        for shift1 in range(shift2 + 1, 13):
            t1, t2 = dedup_blocks(mid, 1 << (shift1 - shift2))
            cost = sum(len(x) * item_size(x) for x in (t1, t2, t3))
            if best is None or cost < best[0]:
                best = (cost, shift1, shift2, t1, t2, t3)
    return best[1:]


def item_size(t):
    m = max(t)
    return 1 if m < 256 else 2 if m < 65536 else 4


def ctype(t):
    return {1: 'unsigned char', 2: 'unsigned short', 4: 'unsigned int'}[item_size(t)]


def emit_array(out, decl, values, per_line=16, fmt='%d'):
    out.write('%s = {\n' % decl)
    for i in range(0, len(values), per_line):
        out.write('    ' + ', '.join(fmt % v for v in values[i:i + per_line]) + ',\n')
    out.write('};\n\n')


def main():
    ext = []
    ext_index = {}
    records = {}
    index = []
    for cp in range(MAXCP):
        rec = properties(cp, ext, ext_index)
        if rec not in records:
            records[rec] = len(records)
        index.append(records[rec])

    shift1, shift2, index1, index2, index3 = split_bins(index)
    assert len(records) < 65536

    header = ('/* Copyright 2005-2026 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE) */\n\n'
              '/* GENERATED by scripts/gen_unicode_db.py from CPython %s (unicode %s) -- do not edit. */\n\n' %
              (sys.version.split()[0], unicodedata.unidata_version))
    recs = sorted(records, key=records.get)
    outdir = sys.argv[1] if len(sys.argv) > 1 else '.'

    with open(os.path.join(outdir, 'unicode_db.hpp'), 'w') as out:
        out.write(header)
        out.write('/* shapes of the tables in unicode_db.cpp, see __ss_char_rec in unicode.hpp */\n\n')
        out.write('#define __SS_UNICODE_VERSION "%s"\n' % unicodedata.unidata_version)
        out.write('#define __SS_UCD_SHIFT1 %d\n' % shift1)
        out.write('#define __SS_UCD_SHIFT2 %d\n\n' % shift2)
        out.write('extern const __ss_char_record __ss_char_records[%d];\n' % len(recs))
        out.write('extern const __ss_char __ss_char_ext_case[%d];\n' % max(1, len(ext)))
        out.write('extern const %s __ss_char_index1[%d];\n' % (ctype(index1), len(index1)))
        out.write('extern const %s __ss_char_index2[%d];\n' % (ctype(index2), len(index2)))
        out.write('extern const %s __ss_char_index3[%d];\n' % (ctype(index3), len(index3)))

    with open(os.path.join(outdir, 'unicode_db.cpp'), 'w') as out:
        out.write(header)
        out.write('/* records: {{upper, lower, title, casefold}, flags, decimal value}; the mappings are deltas\n'
                  '   from the code point itself, or with __SS_CHAR_EXTENDED_CASE set,\n'
                  '   (length << 24) | offset into __ss_char_ext_case */\n\n')
        out.write('const __ss_char_record __ss_char_records[%d] = {\n' % len(recs))
        for flags, decimal, up, lo, ti, fo in recs:
            out.write('    {{%d, %d, %d, %d}, 0x%04x, %d},\n' % (up, lo, ti, fo, flags, decimal))
        out.write('};\n\n')
        emit_array(out, 'const __ss_char __ss_char_ext_case[%d]' % max(1, len(ext)), ext or [0], per_line=8, fmt='0x%04x')
        emit_array(out, 'const %s __ss_char_index1[%d]' % (ctype(index1), len(index1)), index1, per_line=20)
        emit_array(out, 'const %s __ss_char_index2[%d]' % (ctype(index2), len(index2)), index2, per_line=20)
        emit_array(out, 'const %s __ss_char_index3[%d]' % (ctype(index3), len(index3)), index3, per_line=20)

    sys.stderr.write('shifts=%d/%d records=%d ext=%d index sizes=%d/%d/%d\n' % (
        shift1, shift2, len(recs), len(ext), len(index1), len(index2), len(index3)))


if __name__ == '__main__':
    main()
