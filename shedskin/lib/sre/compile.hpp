/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

/* a hand-port of CPython 3.13's Lib/re/_parser.py and Lib/re/_compiler.py,
   producing code for the vendored sre engine (sre_engine.h). it follows the
   python code closely (including error messages and positions), but leaves
   out what shedskin does not need: bytes patterns, the LOCALE flag and DEBUG
   output. */

namespace __re__ {
namespace __sre {

typedef std::vector<SRE_CODE> Code;

enum { MIN_REPEAT = 43, MAX_REPEAT = 44 }; /* parser-only opcodes */
static const uint64_t MAXWIDTH = UINT64_MAX;

struct Seq;

/* (op, av) items of a SubPattern */
struct Node {
    SRE_CODE op;
    SRE_CODE a, b; /* LITERAL etc: a; RANGE/repeats: a-b; SUBPATTERN: group a; ASSERT: dir a */
    int add, del;  /* SUBPATTERN flags */
    std::vector<Node> set; /* IN */
    std::vector<Seq> subs; /* subpatterns (BRANCH items, GROUPREF_EXISTS yes/no, ..) */
    /* defined after Seq: libc++ needs Seq complete to instantiate ~vector<Seq> */
    Node(SRE_CODE op = 0, SRE_CODE a = 0, SRE_CODE b = 0);
    bool operator==(const Node &o) const;
};

struct Seq {
    std::vector<Node> data;
};

inline Node::Node(SRE_CODE op, SRE_CODE a, SRE_CODE b) : op(op), a(a), b(b), add(0), del(0) {}

inline bool Node::operator==(const Node &o) const { /* subpatterns compare by identity in python */
    return op == o.op && a == o.a && b == o.b && set == o.set && subs.empty() && o.subs.empty();
}

static inline uint64_t sat_add(uint64_t x, uint64_t y) { return x > MAXWIDTH - y ? MAXWIDTH : x + y; }
static inline uint64_t sat_mul(uint64_t x, uint64_t y) { return (y && x > MAXWIDTH / y) ? MAXWIDTH : x * y; }

struct State {
    int flags = 0;
    std::vector<std::pair<__GC_STR, int> > groupdict;
    std::vector<std::pair<uint64_t, uint64_t> > groupwidths = {{0, 0}};
    std::vector<bool> closed = {false};
    int lookbehindgroups = -1;
    std::vector<std::pair<SRE_CODE, size_t> > grouprefpos;

    int groups() { return (int)groupwidths.size(); }
    int lookup(const __GC_STR &name) {
        for (auto &p : groupdict)
            if (p.first == name) return p.second;
        return -1;
    }
    bool checkgroup(int gid) { return gid < groups() && closed[gid]; }

    std::pair<uint64_t, uint64_t> getwidth(const Seq &p) {
        uint64_t lo = 0, hi = 0;
        for (const Node &n : p.data) {
            uint64_t i, j;
            switch (n.op) {
            case SRE_OP_BRANCH:
                i = MAXWIDTH; j = 0;
                for (const Seq &s : n.subs) {
                    auto w = getwidth(s);
                    i = std::min(i, w.first); j = std::max(j, w.second);
                }
                lo = sat_add(lo, i); hi = sat_add(hi, j);
                break;
            case SRE_OP_ATOMIC_GROUP: case SRE_OP_SUBPATTERN: {
                auto w = getwidth(n.subs[0]);
                lo = sat_add(lo, w.first); hi = sat_add(hi, w.second);
                break;
            }
            case MIN_REPEAT: case MAX_REPEAT: case SRE_OP_POSSESSIVE_REPEAT: {
                auto w = getwidth(n.subs[0]);
                lo = sat_add(lo, sat_mul(w.first, n.a));
                if (n.b == SRE_MAXREPEAT && w.second) hi = MAXWIDTH;
                else hi = sat_add(hi, sat_mul(w.second, n.b));
                break;
            }
            case SRE_OP_ANY: case SRE_OP_RANGE: case SRE_OP_IN: case SRE_OP_LITERAL:
            case SRE_OP_NOT_LITERAL: case SRE_OP_CATEGORY:
                lo = sat_add(lo, 1); hi = sat_add(hi, 1);
                break;
            case SRE_OP_GROUPREF:
                lo = sat_add(lo, groupwidths[n.a].first); hi = sat_add(hi, groupwidths[n.a].second);
                break;
            case SRE_OP_GROUPREF_EXISTS: {
                auto w = getwidth(n.subs[0]);
                i = w.first; j = w.second;
                if (n.subs.size() > 1) {
                    auto w2 = getwidth(n.subs[1]);
                    i = std::min(i, w2.first); j = std::max(j, w2.second);
                } else
                    i = 0;
                lo = sat_add(lo, i); hi = sat_add(hi, j);
                break;
            }
            }
            if (n.op == SRE_OP_SUCCESS) break;
        }
        return {lo, hi};
    }
};

/* parser */

static bool isdigit_(long c) { return c >= '0' && c <= '9'; }
static bool isoct_(long c) { return c >= '0' && c <= '7'; }
static bool ishex_(long c) { return isdigit_(c) || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F'); }
static bool isletter_(long c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'); }

static __GC_STR S(const char *s) { return __gcs(s); }
static __GC_STR num(uint64_t n) { return __gcs(std::to_string(n)); }

struct Tokenizer {
    str *pattern;
    const __ss_char *s;
    size_t n, index = 0;
    long next = -1; /* None */
    bool esc = false; /* next is a backslash escape */

    Tokenizer(str *p) : pattern(p), s(p->unit.data()), n(p->unit.size()) { advance(); }

    void advance() {
        size_t i = index;
        if (i >= n) { next = -1; esc = false; return; }
        __ss_char c = s[i];
        esc = (c == '\\');
        if (esc && ++i >= n)
            throw new PatternError(new str("bad escape (end of pattern)"), pattern, (__ss_int)n - 1);
        index = i + 1;
        next = s[i];
    }
    bool match(__ss_char c) {
        if (next == (long)c && !esc) { advance(); return true; }
        return false;
    }
    long get(bool *e = 0) { /* -1 if None */
        long c = next;
        if (e) *e = esc;
        advance();
        return c;
    }
    __GC_STR getwhile(int count, bool (*charset)(long)) {
        __GC_STR result;
        for (int i = 0; i < count && !esc && charset(next); i++) {
            result += (__ss_char)next;
            advance();
        }
        return result;
    }
    __GC_STR getuntil(__ss_char terminator, const char *name) {
        __GC_STR result;
        for (;;) {
            bool e;
            long c = get(&e);
            if (c == -1) {
                if (result.empty()) throw error(S("missing ") + S(name));
                throw error(S("missing ") + __GC_STR(1, terminator) + S(", unterminated name"), result.size());
            }
            if (c == (long)terminator && !e) {
                if (result.empty()) throw error(S("missing ") + S(name), 1);
                break;
            }
            if (e) result += '\\';
            result += (__ss_char)c;
        }
        return result;
    }
    size_t tell() { return index - (next == -1 ? 0 : esc ? 2 : 1); }
    void seek(size_t i) { index = i; advance(); }
    PatternError *error(const __GC_STR &msg, size_t offset = 0) {
        return new PatternError(new str(msg), pattern, (__ss_int)(tell() - offset));
    }
    void checkgroupname(const __GC_STR &name, size_t offset) {
        if (!(new str(name))->isidentifier())
            throw error(S("bad character in group name ") + repr(new str(name))->unit, name.size() + offset);
    }
};

static uint64_t to_int(const __GC_STR &s, int base) { /* saturating */
    uint64_t v = 0;
    for (__ss_char c : s) {
        int d = c <= '9' ? c - '0' : (c | 0x20) - 'a' + 10;
        v = sat_add(sat_mul(v, base), d);
    }
    return v;
}

static Node category(SRE_CODE cat) { Node n(SRE_OP_IN); n.set.push_back(Node(SRE_OP_CATEGORY, cat)); return n; }

/* the escapes shared by _class_escape and _escape (\x, \u, \U, \N, ESCAPES) */
static bool common_escape(Tokenizer &source, __GC_STR &escape, __ss_char c, Node &out) {
    const char *esc = "a\007f\014n\012r\015t\011v\013\\\\";
    for (const char *p = esc; *p; p += 2)
        if (c == (__ss_char)p[0]) { out = Node(SRE_OP_LITERAL, (SRE_CODE)(unsigned char)p[1]); return true; }
    if (c == 'x' || c == 'u' || c == 'U') {
        size_t len = c == 'x' ? 2 : c == 'u' ? 4 : 8;
        escape += source.getwhile((int)len, ishex_);
        if (escape.size() != len + 2) throw source.error(S("incomplete escape ") + escape, escape.size());
        uint64_t v = to_int(escape.substr(2), 16);
        if (v > 0x10ffff) throw source.error(S("bad escape ") + escape, escape.size());
        out = Node(SRE_OP_LITERAL, (SRE_CODE)v);
        return true;
    }
    if (c == 'N') { /* there is no unicode name database (yet) */
        if (!source.match('{')) throw source.error(S("missing {"));
        __GC_STR charname = source.getuntil('}', "character name");
        throw source.error(S("\\N{...} escapes are not supported ") + repr(new str(charname))->unit, charname.size() + 4);
    }
    return false;
}

static Node class_escape(Tokenizer &source, __ss_char c) {
    __GC_STR escape = {'\\', c};
    Node out;
    if (c == 'b') return Node(SRE_OP_LITERAL, 8);
    const char *cats = "dDsSwW";
    for (int i = 0; cats[i]; i++)
        if (c == (__ss_char)cats[i]) return category(SRE_CATEGORY_DIGIT + i);
    if (common_escape(source, escape, c, out)) return out;
    if (isoct_(c)) {
        escape += source.getwhile(2, isoct_);
        uint64_t v = to_int(escape.substr(1), 8);
        if (v > 0377)
            throw source.error(S("octal escape value ") + escape + S(" outside of range 0-0o377"), escape.size());
        return Node(SRE_OP_LITERAL, (SRE_CODE)v);
    }
    if (isdigit_(c) || isletter_(c)) throw source.error(S("bad escape ") + escape, escape.size());
    return Node(SRE_OP_LITERAL, c);
}

static Node escape_(Tokenizer &source, __ss_char c, State &state) {
    __GC_STR escape = {'\\', c};
    Node out;
    switch (c) {
    case 'A': return Node(SRE_OP_AT, SRE_AT_BEGINNING_STRING);
    case 'b': return Node(SRE_OP_AT, SRE_AT_BOUNDARY);
    case 'B': return Node(SRE_OP_AT, SRE_AT_NON_BOUNDARY);
    case 'Z': return Node(SRE_OP_AT, SRE_AT_END_STRING);
    }
    const char *cats = "dDsSwW";
    for (int i = 0; cats[i]; i++)
        if (c == (__ss_char)cats[i]) return category(SRE_CATEGORY_DIGIT + i);
    if (common_escape(source, escape, c, out)) return out;
    if (c == '0') {
        escape += source.getwhile(2, isoct_);
        return Node(SRE_OP_LITERAL, (SRE_CODE)to_int(escape.substr(1), 8));
    }
    if (isdigit_(c)) {
        /* octal escape *or* decimal group reference (sigh) */
        if (isdigit_(source.next) && !source.esc) {
            escape += (__ss_char)source.get();
            if (isoct_(escape[1]) && isoct_(escape[2]) && isoct_(source.next) && !source.esc) {
                /* got three octal digits; this is an octal escape */
                escape += (__ss_char)source.get();
                uint64_t v = to_int(escape.substr(1), 8);
                if (v > 0377)
                    throw source.error(S("octal escape value ") + escape + S(" outside of range 0-0o377"), escape.size());
                return Node(SRE_OP_LITERAL, (SRE_CODE)v);
            }
        }
        /* not an octal escape, so this is a group reference */
        int group = (int)to_int(escape.substr(1), 10);
        if (group < state.groups()) {
            if (!state.checkgroup(group)) throw source.error(S("cannot refer to an open group"), escape.size());
            if (state.lookbehindgroups != -1 && group >= state.lookbehindgroups)
                throw source.error(S("cannot refer to group defined in the same lookbehind subpattern"));
            return Node(SRE_OP_GROUPREF, group);
        }
        throw source.error(S("invalid group reference ") + num(group), escape.size() - 1);
    }
    if (isletter_(c)) throw source.error(S("bad escape ") + escape, escape.size());
    return Node(SRE_OP_LITERAL, c);
}

static Seq parse(Tokenizer &source, State &state, bool verbose, int nested, bool first = false);

/* shedskin: limit the nesting depth (of groups, lookarounds, ..), as parsing
   and compiling recurse once per level; CPython hits its recursion limit
   at about 500 levels. each level takes 1-2KB of stack, so this must also
   fit in the 1MB default stack of a Windows thread */
static const int MAXNESTING = 500;

static Seq parse_sub(Tokenizer &source, State &state, bool verbose, int nested) {
    /* parse an alternation: a|b|c */
    if (nested > 2 * MAXNESTING) /* parse() and parse_sub() each add one */
        throw new RecursionError(new str("maximum recursion depth exceeded"));
    std::vector<Seq> items;
    for (;;) {
        items.push_back(parse(source, state, verbose, nested + 1, !nested && items.empty()));
        if (!source.match('|')) break;
        if (!nested) verbose = state.flags & SRE_FLAG_VERBOSE;
    }
    if (items.size() == 1) return items[0];

    Seq subpattern;
    /* check if all items share a common prefix */
    for (;;) {
        bool common = true;
        for (Seq &item : items)
            if (item.data.empty() || !(item.data[0] == items[0].data[0])) { common = false; break; }
        if (!common) break;
        /* all subitems start with a common "prefix". move it out of the branch */
        subpattern.data.push_back(items[0].data[0]);
        for (Seq &item : items) item.data.erase(item.data.begin());
    }

    /* check if the branch can be replaced by a character set */
    std::vector<Node> set;
    bool ok = true;
    for (Seq &item : items) {
        if (item.data.size() != 1) { ok = false; break; }
        Node &n = item.data[0];
        if (n.op == SRE_OP_LITERAL) set.push_back(n);
        else if (n.op == SRE_OP_IN && n.set[0].op != SRE_OP_NEGATE) set.insert(set.end(), n.set.begin(), n.set.end());
        else { ok = false; break; }
    }
    if (ok) {
        Node in(SRE_OP_IN);
        for (Node &n : set) /* _uniq */
            if (std::find(in.set.begin(), in.set.end(), n) == in.set.end()) in.set.push_back(n);
        subpattern.data.push_back(in);
        return subpattern;
    }
    Node branch(SRE_OP_BRANCH);
    branch.subs = items;
    subpattern.data.push_back(branch);
    return subpattern;
}

static const char *FLAGCHARS = "iLmsxau";
static const int FLAGVALUES[] = {SRE_FLAG_IGNORECASE, SRE_FLAG_LOCALE, SRE_FLAG_MULTILINE, SRE_FLAG_DOTALL,
                                 SRE_FLAG_VERBOSE, SRE_FLAG_ASCII, SRE_FLAG_UNICODE};
static const int TYPE_FLAGS = SRE_FLAG_ASCII | SRE_FLAG_LOCALE | SRE_FLAG_UNICODE;

static int flagvalue(long c) {
    for (int i = 0; FLAGCHARS[i]; i++)
        if (c == FLAGCHARS[i]) return FLAGVALUES[i];
    return 0;
}

/* returns false for global flags */
static bool parse_flags(Tokenizer &source, State &state, long c, int &add_flags, int &del_flags) {
    bool e = false;
    add_flags = del_flags = 0;
    if (c != '-') {
        for (;;) {
            int flag = flagvalue(c);
            if (c == 'L') throw source.error(S("bad inline flags: cannot use 'L' flag with a str pattern"));
            add_flags |= flag;
            if ((flag & TYPE_FLAGS) && (add_flags & TYPE_FLAGS) != flag)
                throw source.error(S("bad inline flags: flags 'a', 'u' and 'L' are incompatible"));
            c = source.get(&e);
            if (c == -1) throw source.error(S("missing -, : or )"));
            if (!e && (c == ')' || c == '-' || c == ':')) break;
            if (e || !flagvalue(c))
                throw source.error(S((!e && __ss_char_has((__ss_char)c, __SS_CHAR_ALPHA)) ? "unknown flag" : "missing -, : or )"), e ? 2 : 1);
        }
    }
    if (c == ')') {
        state.flags |= add_flags;
        return false;
    }
    if (c == '-') {
        c = source.get(&e);
        if (c == -1) throw source.error(S("missing flag"));
        if (e || !flagvalue(c))
            throw source.error(S((!e && __ss_char_has((__ss_char)c, __SS_CHAR_ALPHA)) ? "unknown flag" : "missing flag"), e ? 2 : 1);
        for (;;) {
            int flag = flagvalue(c);
            if (flag & TYPE_FLAGS) throw source.error(S("bad inline flags: cannot turn off flags 'a', 'u' and 'L'"));
            del_flags |= flag;
            c = source.get(&e);
            if (c == -1) throw source.error(S("missing :"));
            if (c == ':' && !e) break;
            if (e || !flagvalue(c))
                throw source.error(S((!e && __ss_char_has((__ss_char)c, __SS_CHAR_ALPHA)) ? "unknown flag" : "missing :"), e ? 2 : 1);
        }
    }
    if (add_flags & del_flags) throw source.error(S("bad inline flags: flag turned on and off"), 1);
    return true;
}

static Seq parse(Tokenizer &source, State &state, bool verbose, int nested, bool first) {
    /* parse a simple pattern */
    Seq subpattern;
    std::vector<Node> &data = subpattern.data;

    for (;;) {
        bool esc = source.esc;
        long c = source.next;
        if (c == -1) break; /* end of pattern */
        if (!esc && (c == '|' || c == ')')) break; /* end of subpattern */
        source.get();

        if (verbose && !esc) {
            /* skip whitespace and comments */
            if (c == ' ' || (c >= '\t' && c <= '\r')) continue;
            if (c == '#') {
                for (;;) {
                    bool e;
                    long d = source.get(&e);
                    if (d == -1 || (d == '\n' && !e)) break;
                }
                continue;
            }
        }

        if (esc) {
            data.push_back(escape_(source, (__ss_char)c, state));

        } else if (!strchr(".[{()*+?^$|", (int)c) || c == 0 || c > 127) {
            data.push_back(Node(SRE_OP_LITERAL, (SRE_CODE)c));

        } else if (c == '[') {
            size_t here = source.tell() - 1;
            /* character set */
            std::vector<Node> set;
            bool negate = source.match('^');
            /* check remaining characters */
            for (;;) {
                bool e;
                long d = source.get(&e);
                if (d == -1) throw source.error(S("unterminated character set"), source.tell() - here);
                Node code1;
                if (d == ']' && !e && !set.empty()) break;
                else if (e) code1 = class_escape(source, (__ss_char)d);
                else code1 = Node(SRE_OP_LITERAL, (SRE_CODE)d);
                if (source.match('-')) {
                    /* potential range */
                    bool e2;
                    long that = source.get(&e2);
                    if (that == -1) throw source.error(S("unterminated character set"), source.tell() - here);
                    if (that == ']' && !e2) {
                        if (code1.op == SRE_OP_IN) code1 = code1.set[0];
                        set.push_back(code1);
                        set.push_back(Node(SRE_OP_LITERAL, '-'));
                        break;
                    }
                    Node code2 = e2 ? class_escape(source, (__ss_char)that) : Node(SRE_OP_LITERAL, (SRE_CODE)that);
                    if (code1.op != SRE_OP_LITERAL || code2.op != SRE_OP_LITERAL || code2.a < code1.a) {
                        __GC_STR msg = S("bad character range ");
                        if (e) msg += '\\';
                        msg += (__ss_char)d;
                        msg += '-';
                        if (e2) msg += '\\';
                        msg += (__ss_char)that;
                        throw source.error(msg, (e ? 2 : 1) + 1 + (e2 ? 2 : 1));
                    }
                    set.push_back(Node(SRE_OP_RANGE, code1.a, code2.a));
                } else {
                    if (code1.op == SRE_OP_IN) code1 = code1.set[0];
                    set.push_back(code1);
                }
            }
            std::vector<Node> uniq;
            for (Node &n : set)
                if (std::find(uniq.begin(), uniq.end(), n) == uniq.end()) uniq.push_back(n);
            if (uniq.size() == 1 && uniq[0].op == SRE_OP_LITERAL) {
                /* optimization */
                data.push_back(negate ? Node(SRE_OP_NOT_LITERAL, uniq[0].a) : uniq[0]);
            } else {
                if (negate) uniq.insert(uniq.begin(), Node(SRE_OP_NEGATE));
                Node in(SRE_OP_IN);
                in.set = uniq;
                data.push_back(in);
            }

        } else if (c == '*' || c == '+' || c == '?' || c == '{') {
            /* repeat previous item */
            size_t here = source.tell();
            uint64_t min = 0, max = SRE_MAXREPEAT;
            if (c == '?') max = 1;
            else if (c == '+') min = 1;
            else if (c == '{') {
                if (source.next == '}' && !source.esc) {
                    data.push_back(Node(SRE_OP_LITERAL, '{'));
                    continue;
                }
                __GC_STR lo, hi;
                while (isdigit_(source.next) && !source.esc) lo += (__ss_char)source.get();
                if (source.match(',')) {
                    while (isdigit_(source.next) && !source.esc) hi += (__ss_char)source.get();
                } else
                    hi = lo;
                if (!source.match('}')) {
                    data.push_back(Node(SRE_OP_LITERAL, '{'));
                    source.seek(here);
                    continue;
                }
                if (!lo.empty()) {
                    min = to_int(lo, 10);
                    if (min >= SRE_MAXREPEAT) throw new OverflowError(new str("the repetition number is too large"));
                }
                if (!hi.empty()) {
                    max = to_int(hi, 10);
                    if (max >= SRE_MAXREPEAT) throw new OverflowError(new str("the repetition number is too large"));
                    if (max < min) throw source.error(S("min repeat greater than max repeat"), source.tell() - here);
                }
            }
            /* figure out which item to repeat */
            if (data.empty() || data.back().op == SRE_OP_AT)
                throw source.error(S("nothing to repeat"), source.tell() - here + 1);
            SRE_CODE last = data.back().op;
            if (last == MIN_REPEAT || last == MAX_REPEAT || last == SRE_OP_POSSESSIVE_REPEAT)
                throw source.error(S("multiple repeat"), source.tell() - here + 1);
            Seq item;
            Node &b = data.back();
            if (b.op == SRE_OP_SUBPATTERN && b.a == 0 && !b.add && !b.del) item = b.subs[0];
            else item.data.push_back(b);
            SRE_CODE op = MAX_REPEAT;
            if (source.match('?')) op = MIN_REPEAT; /* Non-Greedy Match */
            else if (source.match('+')) op = SRE_OP_POSSESSIVE_REPEAT; /* Possessive Match (Always Greedy) */
            Node rep(op, (SRE_CODE)min, (SRE_CODE)max);
            rep.subs.push_back(item);
            data.back() = rep;

        } else if (c == '.') {
            data.push_back(Node(SRE_OP_ANY));

        } else if (c == '(') {
            size_t start = source.tell() - 1;
            bool capture = true, atomic = false, e;
            __GC_STR name;
            bool named = false;
            int add_flags = 0, del_flags = 0;
            if (source.match('?')) {
                /* options */
                long d = source.get(&e);
                if (d == -1) throw source.error(S("unexpected end of pattern"));
                if (d == 'P' && !e) {
                    /* python extensions */
                    if (source.match('<')) {
                        /* named group: skip forward to end of name */
                        name = source.getuntil('>', "group name");
                        named = true;
                        source.checkgroupname(name, 1);
                    } else if (source.match('=')) {
                        /* named backreference */
                        name = source.getuntil(')', "group name");
                        source.checkgroupname(name, 1);
                        int gid = state.lookup(name);
                        if (gid == -1) throw source.error(S("unknown group name ") + repr(new str(name))->unit, name.size() + 1);
                        if (!state.checkgroup(gid)) throw source.error(S("cannot refer to an open group"), name.size() + 1);
                        if (state.lookbehindgroups != -1 && gid >= state.lookbehindgroups)
                            throw source.error(S("cannot refer to group defined in the same lookbehind subpattern"));
                        data.push_back(Node(SRE_OP_GROUPREF, gid));
                        continue;
                    } else {
                        long f = source.get(&e);
                        if (f == -1) throw source.error(S("unexpected end of pattern"));
                        __GC_STR msg = S("unknown extension ?P");
                        if (e) msg += '\\';
                        msg += (__ss_char)f;
                        throw source.error(msg, (e ? 2 : 1) + 2);
                    }
                } else if (d == ':' && !e) {
                    /* non-capturing group */
                    capture = false;
                } else if (d == '#' && !e) {
                    /* comment */
                    for (;;) {
                        if (source.next == -1)
                            throw source.error(S("missing ), unterminated comment"), source.tell() - start);
                        bool e2;
                        if (source.get(&e2) == ')' && !e2) break;
                    }
                    continue;
                } else if ((d == '=' || d == '!' || d == '<') && !e) {
                    /* lookahead assertions */
                    int dir = 1, lookbehindgroups = -2;
                    if (d == '<') {
                        d = source.get(&e);
                        if (d == -1) throw source.error(S("unexpected end of pattern"));
                        if (e || (d != '=' && d != '!')) {
                            __GC_STR msg = S("unknown extension ?<");
                            if (e) msg += '\\';
                            msg += (__ss_char)d;
                            throw source.error(msg, (e ? 2 : 1) + 2);
                        }
                        dir = -1; /* lookbehind */
                        lookbehindgroups = state.lookbehindgroups;
                        if (lookbehindgroups == -1) state.lookbehindgroups = state.groups();
                    }
                    Seq p = parse_sub(source, state, verbose, nested + 1);
                    if (dir < 0 && lookbehindgroups == -1) state.lookbehindgroups = -1;
                    if (!source.match(')')) throw source.error(S("missing ), unterminated subpattern"), source.tell() - start);
                    if (d == '=') {
                        Node n(SRE_OP_ASSERT, (SRE_CODE)dir);
                        n.subs.push_back(p);
                        data.push_back(n);
                    } else if (!p.data.empty()) {
                        Node n(SRE_OP_ASSERT_NOT, (SRE_CODE)dir);
                        n.subs.push_back(p);
                        data.push_back(n);
                    } else
                        data.push_back(Node(SRE_OP_FAILURE));
                    continue;
                } else if (d == '(' && !e) {
                    /* conditional backreference group */
                    __GC_STR condname = source.getuntil(')', "group name");
                    int condgroup;
                    bool decimal = true;
                    for (__ss_char ch : condname) decimal = decimal && isdigit_(ch);
                    if (!decimal) {
                        source.checkgroupname(condname, 1);
                        condgroup = state.lookup(condname);
                        if (condgroup == -1)
                            throw source.error(S("unknown group name ") + repr(new str(condname))->unit, condname.size() + 1);
                    } else {
                        uint64_t g = to_int(condname, 10);
                        if (!g) throw source.error(S("bad group number"), condname.size() + 1);
                        if (g >= SRE_MAXGROUPS) throw source.error(S("invalid group reference ") + num(g), condname.size() + 1);
                        condgroup = (int)g;
                        bool seen = false;
                        for (auto &p : state.grouprefpos) seen = seen || p.first == (SRE_CODE)condgroup;
                        if (!seen) state.grouprefpos.push_back({(SRE_CODE)condgroup, source.tell() - condname.size() - 1});
                    }
                    if (state.lookbehindgroups != -1) {
                        if (!state.checkgroup(condgroup)) throw source.error(S("cannot refer to an open group"));
                        if (condgroup >= state.lookbehindgroups)
                            throw source.error(S("cannot refer to group defined in the same lookbehind subpattern"));
                    }
                    Node n(SRE_OP_GROUPREF_EXISTS, (SRE_CODE)condgroup);
                    n.subs.push_back(parse(source, state, verbose, nested + 1));
                    if (source.match('|')) {
                        n.subs.push_back(parse(source, state, verbose, nested + 1));
                        if (source.next == '|' && !source.esc) throw source.error(S("conditional backref with more than two branches"));
                    }
                    if (!source.match(')')) throw source.error(S("missing ), unterminated subpattern"), source.tell() - start);
                    data.push_back(n);
                    continue;
                } else if (d == '>' && !e) {
                    /* non-capturing, atomic group */
                    capture = false;
                    atomic = true;
                } else if (!e && (flagvalue(d) || d == '-')) {
                    /* flags */
                    if (!parse_flags(source, state, d, add_flags, del_flags)) { /* global flags */
                        if (!first || !data.empty())
                            throw source.error(S("global flags not at the start of the expression"), source.tell() - start);
                        verbose = state.flags & SRE_FLAG_VERBOSE;
                        continue;
                    }
                    capture = false;
                } else {
                    __GC_STR msg = S("unknown extension ?");
                    if (e) msg += '\\';
                    msg += (__ss_char)d;
                    throw source.error(msg, (e ? 2 : 1) + 1);
                }
            }

            /* parse group contents */
            int group = 0;
            if (capture) {
                group = state.groups();
                state.groupwidths.push_back({0, 0});
                state.closed.push_back(false);
                if ((SRE_CODE)state.groups() > SRE_MAXGROUPS) throw source.error(S("too many groups"), name.size() + 1);
                if (named) {
                    int ogid = state.lookup(name);
                    if (ogid != -1)
                        throw source.error(S("redefinition of group name ") + repr(new str(name))->unit + S(" as group ") + num(group) + S("; was group ") + num(ogid), name.size() + 1);
                    state.groupdict.push_back({name, group});
                }
            }
            bool sub_verbose = (verbose || (add_flags & SRE_FLAG_VERBOSE)) && !(del_flags & SRE_FLAG_VERBOSE);
            Seq p = parse_sub(source, state, sub_verbose, nested + 1);
            if (!source.match(')')) throw source.error(S("missing ), unterminated subpattern"), source.tell() - start);
            if (group) {
                state.groupwidths[group] = state.getwidth(p);
                state.closed[group] = true;
            }
            Node n(atomic ? SRE_OP_ATOMIC_GROUP : SRE_OP_SUBPATTERN, (SRE_CODE)group);
            n.add = add_flags;
            n.del = del_flags;
            n.subs.push_back(p);
            data.push_back(n);

        } else if (c == '^') {
            data.push_back(Node(SRE_OP_AT, SRE_AT_BEGINNING));

        } else if (c == '$') {
            data.push_back(Node(SRE_OP_AT, SRE_AT_END));
        }
    }

    /* unpack non-capturing groups */
    for (size_t i = data.size(); i-- > 0;) {
        Node &n = data[i];
        if (n.op == SRE_OP_SUBPATTERN && n.a == 0 && !n.add && !n.del) {
            std::vector<Node> inner = n.subs[0].data;
            data.erase(data.begin() + i);
            data.insert(data.begin() + i, inner.begin(), inner.end());
        }
    }
    return subpattern;
}

/* compiler */

static const SRE_CODE EXTRA_CASES[][3] = { /* re/_casefix.py */
    {0x0069, 0x0131, 0}, {0x0073, 0x017f, 0}, {0x00b5, 0x03bc, 0}, {0x0131, 0x0069, 0},
    {0x017f, 0x0073, 0}, {0x0345, 0x03b9, 0x1fbe}, {0x0390, 0x1fd3, 0}, {0x03b0, 0x1fe3, 0},
    {0x03b2, 0x03d0, 0}, {0x03b5, 0x03f5, 0}, {0x03b8, 0x03d1, 0}, {0x03b9, 0x0345, 0x1fbe},
    {0x03ba, 0x03f0, 0}, {0x03bc, 0x00b5, 0}, {0x03c0, 0x03d6, 0}, {0x03c1, 0x03f1, 0},
    {0x03c2, 0x03c3, 0}, {0x03c3, 0x03c2, 0}, {0x03c6, 0x03d5, 0}, {0x03d0, 0x03b2, 0},
    {0x03d1, 0x03b8, 0}, {0x03d5, 0x03c6, 0}, {0x03d6, 0x03c0, 0}, {0x03f0, 0x03ba, 0},
    {0x03f1, 0x03c1, 0}, {0x03f5, 0x03b5, 0}, {0x0432, 0x1c80, 0}, {0x0434, 0x1c81, 0},
    {0x043e, 0x1c82, 0}, {0x0441, 0x1c83, 0}, {0x0442, 0x1c84, 0x1c85}, {0x044a, 0x1c86, 0},
    {0x0463, 0x1c87, 0}, {0x1c80, 0x0432, 0}, {0x1c81, 0x0434, 0}, {0x1c82, 0x043e, 0},
    {0x1c83, 0x0441, 0}, {0x1c84, 0x0442, 0x1c85}, {0x1c85, 0x0442, 0x1c84}, {0x1c86, 0x044a, 0},
    {0x1c87, 0x0463, 0}, {0x1c88, 0xa64b, 0}, {0x1e61, 0x1e9b, 0}, {0x1e9b, 0x1e61, 0},
    {0x1fbe, 0x0345, 0x03b9}, {0x1fd3, 0x0390, 0}, {0x1fe3, 0x03b0, 0}, {0xa64b, 0x1c88, 0},
    {0xfb05, 0xfb06, 0}, {0xfb06, 0xfb05, 0},
};

static const SRE_CODE *fixes_for(SRE_CODE c) {
    for (auto &f : EXTRA_CASES)
        if (f[0] == c) return f + 1;
    return 0;
}

struct Case { /* iscased/tolower/fixes, depending on the flags */
    bool unicode;
    bool iscased(SRE_CODE c) {
        if (!unicode) return c < 128 && isletter_(c);
        return c != sre_lower_unicode(c) || c != sre_upper_unicode(c);
    }
    SRE_CODE lower(SRE_CODE c) { return unicode ? sre_lower_unicode(c) : sre_lower_ascii(c); }
};

static void mk_bitmap(const std::vector<unsigned char> &bits, Code &out) {
    for (size_t i = 0; i < bits.size(); i += 32) {
        SRE_CODE w = 0;
        for (int j = 0; j < 32; j++)
            if (bits[i + j]) w |= (SRE_CODE)1 << j;
        out.push_back(w);
    }
}

/* internal: optimize character set */
static std::vector<Node> optimize_charset(const std::vector<Node> &charset, Case *fixup, bool &hascased) {
    std::vector<Node> out, tail;
    std::vector<unsigned char> charmap(256);
    hascased = false;
    bool fixes = fixup && fixup->unicode;
    for (Node item : charset) {
        for (;;) {
            /* returns false where python raises IndexError */
            auto setmap = [&](SRE_CODE i) {
                if (i >= charmap.size()) return false;
                charmap[i] = 1;
                if (fixes) {
                    const SRE_CODE *f = fixes_for(i);
                    if (f)
                        for (int k = 0; k < 2 && f[k]; k++) {
                            if (f[k] >= charmap.size()) return false;
                            charmap[f[k]] = 1;
                        }
                }
                return true;
            };
            bool ok = true;
            if (item.op == SRE_OP_LITERAL) {
                if (fixup) {
                    item.a = fixup->lower(item.a);
                    ok = setmap(item.a);
                    if (ok && !hascased && fixup->iscased(item.a)) hascased = true;
                } else
                    ok = setmap(item.a);
            } else if (item.op == SRE_OP_RANGE) {
                for (SRE_CODE i = item.a; ok && i <= item.b; i++) {
                    ok = setmap(fixup ? fixup->lower(i) : i);
                    if (i == item.b) break;
                }
                if (ok && fixup && !hascased)
                    for (SRE_CODE i = item.a; !hascased; i++) {
                        hascased = fixup->iscased(i);
                        if (i == item.b) break;
                    }
            } else if (item.op == SRE_OP_NEGATE) {
                out.push_back(item);
            } else
                tail.push_back(item);
            if (ok) break;
            if (charmap.size() == 256) {
                /* character set contains non-UCS1 character codes */
                charmap.resize(65536);
                continue;
            }
            /* character set contains non-BMP character codes */
            if (fixup) {
                if (item.op == SRE_OP_RANGE) {
                    if (fixes) item.op = SRE_OP_RANGE_UNI_IGNORE;
                    hascased = true;
                } else if (!hascased && fixup->iscased(item.a))
                    hascased = true;
            }
            tail.push_back(item);
            break;
        }
    }

    /* compress character map */
    std::vector<std::pair<size_t, size_t> > runs;
    bool use_runs = true;
    size_t q = 0;
    for (;;) {
        size_t p = q;
        while (p < charmap.size() && !charmap[p]) p++;
        if (p == charmap.size()) break;
        if (runs.size() >= 2) { use_runs = false; break; }
        q = p;
        while (q < charmap.size() && charmap[q]) q++;
        runs.push_back({p, q});
        if (q == charmap.size()) break;
    }
    if (use_runs) {
        /* use literal/range */
        for (auto &r : runs) {
            if (r.second - r.first == 1) out.push_back(Node(SRE_OP_LITERAL, (SRE_CODE)r.first));
            else out.push_back(Node(SRE_OP_RANGE, (SRE_CODE)r.first, (SRE_CODE)(r.second - 1)));
        }
        out.insert(out.end(), tail.begin(), tail.end());
        /* if the case was changed or new representation is more compact */
        if (hascased || out.size() < charset.size()) return out;
        /* else original character set is good enough */
        return charset;
    }

    Node bits(SRE_OP_CHARSET);
    Code data;
    if (charmap.size() == 256) {
        /* use bitmap */
        mk_bitmap(charmap, data);
    } else {
        /* To represent a big charset, first a bitmap of all characters in the
           set is constructed. Then, this bitmap is sliced into chunks of 256
           characters, duplicate chunks are eliminated, and each chunk is
           given a number. */
        bits.op = SRE_OP_BIGCHARSET;
        std::vector<std::vector<unsigned char> > comps;
        unsigned char mapping[256];
        std::vector<unsigned char> chunks;
        for (size_t i = 0; i < 65536; i += 256) {
            std::vector<unsigned char> chunk(charmap.begin() + i, charmap.begin() + i + 256);
            size_t k = std::find(comps.begin(), comps.end(), chunk) - comps.begin();
            if (k == comps.size()) {
                comps.push_back(chunk);
                chunks.insert(chunks.end(), chunk.begin(), chunk.end());
            }
            mapping[i / 256] = (unsigned char)k;
        }
        data.push_back((SRE_CODE)comps.size());
        SRE_CODE words[64];
        memcpy(words, mapping, 256);
        data.insert(data.end(), words, words + 64);
        mk_bitmap(chunks, data);
    }
    std::vector<Node> result = out;
    bits.set.resize(data.size()); /* bitmap words, stored in .a */
    for (size_t i = 0; i < data.size(); i++) bits.set[i].a = data[i];
    result.push_back(bits);
    result.insert(result.end(), tail.begin(), tail.end());
    return result;
}

static void compile_charset(const std::vector<Node> &charset, int flags, Code &code) {
    /* compile charset subprogram */
    for (const Node &n : charset) {
        code.push_back(n.op);
        switch (n.op) {
        case SRE_OP_LITERAL: code.push_back(n.a); break;
        case SRE_OP_RANGE: case SRE_OP_RANGE_UNI_IGNORE: code.push_back(n.a); code.push_back(n.b); break;
        case SRE_OP_CHARSET: case SRE_OP_BIGCHARSET: for (const Node &w : n.set) code.push_back(w.a); break;
        case SRE_OP_CATEGORY: code.push_back(flags & SRE_FLAG_UNICODE ? n.a + SRE_CATEGORY_UNI_DIGIT : n.a); break;
        }
    }
    code.push_back(SRE_OP_FAILURE);
}

static bool simple(const Seq &p) {
    /* check if this subpattern is a "simple" operator */
    if (p.data.size() != 1) return false;
    const Node &n = p.data[0];
    if (n.op == SRE_OP_SUBPATTERN) return n.a == 0 && simple(n.subs[0]);
    return n.op == SRE_OP_ANY || n.op == SRE_OP_IN || n.op == SRE_OP_LITERAL || n.op == SRE_OP_NOT_LITERAL;
}

static void compile(Code &code, const Seq &pattern, int flags, State &state) {
    /* internal: compile a (sub)pattern */
    Case case_ = {(flags & SRE_FLAG_UNICODE) != 0};
    bool ignore = flags & SRE_FLAG_IGNORECASE;
    for (const Node &n : pattern.data) {
        size_t skip;
        switch (n.op) {
        case SRE_OP_LITERAL: case SRE_OP_NOT_LITERAL:
            if (!ignore || !case_.iscased(n.a)) {
                code.push_back(n.op);
                code.push_back(n.a);
            } else {
                SRE_CODE lo = case_.lower(n.a);
                const SRE_CODE *f = case_.unicode ? fixes_for(lo) : 0;
                if (!case_.unicode) {
                    code.push_back(n.op == SRE_OP_LITERAL ? SRE_OP_LITERAL_IGNORE : SRE_OP_NOT_LITERAL_IGNORE);
                    code.push_back(lo);
                } else if (!f) {
                    code.push_back(n.op == SRE_OP_LITERAL ? SRE_OP_LITERAL_UNI_IGNORE : SRE_OP_NOT_LITERAL_UNI_IGNORE);
                    code.push_back(lo);
                } else {
                    code.push_back(SRE_OP_IN_UNI_IGNORE);
                    skip = code.size(); code.push_back(0);
                    if (n.op == SRE_OP_NOT_LITERAL) code.push_back(SRE_OP_NEGATE);
                    code.push_back(SRE_OP_LITERAL); code.push_back(lo);
                    for (int k = 0; k < 2 && f[k]; k++) { code.push_back(SRE_OP_LITERAL); code.push_back(f[k]); }
                    code.push_back(SRE_OP_FAILURE);
                    code[skip] = (SRE_CODE)(code.size() - skip);
                }
            }
            break;
        case SRE_OP_IN: {
            bool hascased;
            std::vector<Node> charset = optimize_charset(n.set, ignore ? &case_ : 0, hascased);
            if (!hascased) code.push_back(SRE_OP_IN);
            else if (!case_.unicode) code.push_back(SRE_OP_IN_IGNORE);
            else code.push_back(SRE_OP_IN_UNI_IGNORE);
            skip = code.size(); code.push_back(0);
            compile_charset(charset, flags, code);
            code[skip] = (SRE_CODE)(code.size() - skip);
            break;
        }
        case SRE_OP_ANY:
            code.push_back(flags & SRE_FLAG_DOTALL ? SRE_OP_ANY_ALL : SRE_OP_ANY);
            break;
        case MIN_REPEAT: case MAX_REPEAT: case SRE_OP_POSSESSIVE_REPEAT: {
            SRE_CODE ops[3] = {SRE_OP_REPEAT, SRE_OP_MAX_UNTIL, SRE_OP_REPEAT_ONE};
            if (n.op == MIN_REPEAT) ops[1] = SRE_OP_MIN_UNTIL, ops[2] = SRE_OP_MIN_REPEAT_ONE;
            if (n.op == SRE_OP_POSSESSIVE_REPEAT)
                ops[0] = SRE_OP_POSSESSIVE_REPEAT, ops[1] = SRE_OP_SUCCESS, ops[2] = SRE_OP_POSSESSIVE_REPEAT_ONE;
            bool simple_ = simple(n.subs[0]);
            code.push_back(simple_ ? ops[2] : ops[0]);
            skip = code.size(); code.push_back(0);
            code.push_back(n.a);
            code.push_back(n.b);
            compile(code, n.subs[0], flags, state);
            if (simple_) code.push_back(SRE_OP_SUCCESS);
            code[skip] = (SRE_CODE)(code.size() - skip);
            if (!simple_) code.push_back(ops[1]);
            break;
        }
        case SRE_OP_SUBPATTERN: {
            int flags2 = flags;
            if (n.add & TYPE_FLAGS) flags2 &= ~TYPE_FLAGS;
            flags2 = (flags2 | n.add) & ~n.del;
            if (n.a) { code.push_back(SRE_OP_MARK); code.push_back((n.a - 1) * 2); }
            compile(code, n.subs[0], flags2, state);
            if (n.a) { code.push_back(SRE_OP_MARK); code.push_back((n.a - 1) * 2 + 1); }
            break;
        }
        case SRE_OP_ATOMIC_GROUP:
            code.push_back(SRE_OP_ATOMIC_GROUP);
            skip = code.size(); code.push_back(0);
            compile(code, n.subs[0], flags, state);
            code.push_back(SRE_OP_SUCCESS);
            code[skip] = (SRE_CODE)(code.size() - skip);
            break;
        case SRE_OP_SUCCESS: case SRE_OP_FAILURE:
            code.push_back(n.op);
            break;
        case SRE_OP_ASSERT: case SRE_OP_ASSERT_NOT:
            code.push_back(n.op);
            skip = code.size(); code.push_back(0);
            if (n.a == 1) /* look ahead */
                code.push_back(0);
            else {
                auto w = state.getwidth(n.subs[0]);
                if (w.first > 0xffffffffULL) throw new PatternError(new str("looks too much behind"));
                if (w.first != w.second) throw new PatternError(new str("look-behind requires fixed-width pattern"));
                code.push_back((SRE_CODE)w.first); /* look behind */
            }
            compile(code, n.subs[0], flags, state);
            code.push_back(SRE_OP_SUCCESS);
            code[skip] = (SRE_CODE)(code.size() - skip);
            break;
        case SRE_OP_AT: {
            SRE_CODE at = n.a;
            if (flags & SRE_FLAG_MULTILINE) {
                if (at == SRE_AT_BEGINNING) at = SRE_AT_BEGINNING_LINE;
                else if (at == SRE_AT_END) at = SRE_AT_END_LINE;
            }
            if (flags & SRE_FLAG_UNICODE) {
                if (at == SRE_AT_BOUNDARY) at = SRE_AT_UNI_BOUNDARY;
                else if (at == SRE_AT_NON_BOUNDARY) at = SRE_AT_UNI_NON_BOUNDARY;
            }
            code.push_back(SRE_OP_AT);
            code.push_back(at);
            break;
        }
        case SRE_OP_BRANCH: {
            code.push_back(SRE_OP_BRANCH);
            std::vector<size_t> tail;
            for (const Seq &alt : n.subs) {
                skip = code.size(); code.push_back(0);
                compile(code, alt, flags, state);
                code.push_back(SRE_OP_JUMP);
                tail.push_back(code.size()); code.push_back(0);
                code[skip] = (SRE_CODE)(code.size() - skip);
            }
            code.push_back(SRE_OP_FAILURE); /* end of branch */
            for (size_t t : tail) code[t] = (SRE_CODE)(code.size() - t);
            break;
        }
        case SRE_OP_GROUPREF:
            code.push_back(!ignore ? SRE_OP_GROUPREF : case_.unicode ? SRE_OP_GROUPREF_UNI_IGNORE : SRE_OP_GROUPREF_IGNORE);
            code.push_back(n.a - 1);
            break;
        case SRE_OP_GROUPREF_EXISTS: {
            code.push_back(SRE_OP_GROUPREF_EXISTS);
            code.push_back(n.a - 1);
            size_t skipyes = code.size(); code.push_back(0);
            compile(code, n.subs[0], flags, state);
            if (n.subs.size() > 1 && !n.subs[1].data.empty()) { /* an empty 'no' branch is falsy */
                code.push_back(SRE_OP_JUMP);
                size_t skipno = code.size(); code.push_back(0);
                code[skipyes] = (SRE_CODE)(code.size() - skipyes + 1);
                compile(code, n.subs[1], flags, state);
                code[skipno] = (SRE_CODE)(code.size() - skipno);
            } else
                code[skipyes] = (SRE_CODE)(code.size() - skipyes + 1);
            break;
        }
        }
    }
}

/* the INFO block (a search optimization) */

static bool iscased_(int flags, SRE_CODE c) {
    Case case_ = {(flags & SRE_FLAG_UNICODE) != 0};
    return (flags & SRE_FLAG_IGNORECASE) && case_.iscased(c);
}

static int combine_flags(int flags, int add, int del) {
    if (add & TYPE_FLAGS) flags &= ~TYPE_FLAGS;
    return (flags | add) & ~del;
}

/* look for literal prefix; returns got_all, prefix_skip -1 is None */
static bool get_literal_prefix(const Seq &pattern, int flags, std::vector<SRE_CODE> &prefix, long &prefix_skip) {
    for (const Node &n : pattern.data) {
        if (n.op == SRE_OP_LITERAL) {
            if (iscased_(flags, n.a)) return false;
            prefix.push_back(n.a);
        } else if (n.op == SRE_OP_SUBPATTERN) {
            std::vector<SRE_CODE> prefix1;
            long prefix_skip1 = -1;
            bool got_all = get_literal_prefix(n.subs[0], combine_flags(flags, n.add, n.del), prefix1, prefix_skip1);
            if (prefix_skip == -1) {
                if (n.a) prefix_skip = (long)prefix.size();
                else if (prefix_skip1 != -1) prefix_skip = (long)prefix.size() + prefix_skip1;
            }
            prefix.insert(prefix.end(), prefix1.begin(), prefix1.end());
            if (!got_all) return false;
        } else
            return false;
    }
    return true;
}

static bool get_charset_prefix(const Seq *pattern, int flags, std::vector<Node> &charset) {
    const Node *n;
    for (;;) {
        if (pattern->data.empty()) return false;
        n = &pattern->data[0];
        if (n->op != SRE_OP_SUBPATTERN) break;
        flags = combine_flags(flags, n->add, n->del);
        pattern = &n->subs[0];
    }
    if (n->op == SRE_OP_LITERAL) {
        if (iscased_(flags, n->a)) return false;
        charset.push_back(*n);
        return true;
    } else if (n->op == SRE_OP_BRANCH) {
        std::vector<Node> literals;
        for (const Seq &p : n->subs) {
            if (p.data.empty() || p.data[0].op != SRE_OP_LITERAL || iscased_(flags, p.data[0].a)) return false;
            literals.push_back(p.data[0]);
        }
        charset = literals;
        return true;
    } else if (n->op == SRE_OP_IN) {
        for (const Node &m : n->set) {
            if (m.op == SRE_OP_LITERAL && iscased_(flags, m.a)) return false;
            if (m.op == SRE_OP_RANGE && (flags & SRE_FLAG_IGNORECASE)) {
                if (m.b > 0xffff) return false;
                for (SRE_CODE c = m.a; c <= m.b; c++)
                    if (iscased_(flags, c)) return false;
            }
        }
        charset = n->set;
        return true;
    }
    return false;
}

static void compile_info(Code &code, const Seq &pattern, int flags, State &state) {
    /* internal: compile an info block.  in the current version,
       this contains min/max pattern width, and an optional literal
       prefix or a character map */
    auto w = state.getwidth(pattern);
    uint64_t lo = w.first, hi = std::min<uint64_t>(w.second, 0xffffffffULL);
    if (lo == 0) {
        code.insert(code.end(), {SRE_OP_INFO, 4, 0, (SRE_CODE)lo, (SRE_CODE)hi});
        return;
    }
    /* look for a literal prefix, and if none, for a charset prefix */
    std::vector<SRE_CODE> prefix;
    long prefix_skip = -1;
    std::vector<Node> charset;
    bool got_all = get_literal_prefix(pattern, flags, prefix, prefix_skip);
    if (prefix.empty()) get_charset_prefix(&pattern, flags, charset);
    /* add an info block */
    code.push_back(SRE_OP_INFO);
    size_t skip = code.size(); code.push_back(0);
    SRE_CODE mask = 0;
    if (!prefix.empty()) {
        mask = SRE_INFO_PREFIX;
        if (prefix_skip == -1 && got_all) mask |= SRE_INFO_LITERAL;
    } else if (!charset.empty())
        mask |= SRE_INFO_CHARSET;
    code.push_back(mask);
    /* pattern length */
    if (lo < 0xffffffffULL)
        code.push_back((SRE_CODE)lo);
    else {
        code.push_back(0xffffffff);
        if (prefix.size() > 0xffffffffULL) prefix.resize(0xffffffff);
    }
    code.push_back((SRE_CODE)hi);
    if (!prefix.empty()) {
        /* add literal prefix */
        code.push_back((SRE_CODE)prefix.size());
        if (prefix_skip == -1) prefix_skip = (long)prefix.size();
        code.push_back((SRE_CODE)prefix_skip);
        code.insert(code.end(), prefix.begin(), prefix.end());
        /* generate overlap table */
        std::vector<SRE_CODE> table(prefix.size());
        for (size_t i = 1; i < prefix.size(); i++) {
            SRE_CODE idx = table[i - 1];
            for (;;) {
                if (prefix[i] == prefix[idx]) { table[i] = idx + 1; break; }
                if (idx == 0) { table[i] = 0; break; }
                idx = table[idx - 1];
            }
        }
        code.insert(code.end(), table.begin(), table.end());
    } else if (!charset.empty()) {
        bool hascased;
        compile_charset(optimize_charset(charset, 0, hascased), flags, code);
    }
    code[skip] = (SRE_CODE)(code.size() - skip);
}

/* parse and compile a pattern; fills in the code, the final flags, the
   number of groups and the named groups (in order of definition) */
static void compile_pattern(str *pattern, int flags, Code &code, int &outflags, int &groups,
                            std::vector<std::pair<__GC_STR, int> > &groupindex) {
    Tokenizer source(pattern);
    State state;
    state.flags = flags;
    Seq p = parse_sub(source, state, flags & SRE_FLAG_VERBOSE, 0);

    /* fix_flags */
    if (state.flags & SRE_FLAG_LOCALE) throw new ValueError(new str("cannot use LOCALE flag with a str pattern"));
    if (!(state.flags & SRE_FLAG_ASCII)) state.flags |= SRE_FLAG_UNICODE;
    else if (state.flags & SRE_FLAG_UNICODE) throw new ValueError(new str("ASCII and UNICODE flags are incompatible"));

    if (source.next != -1) throw source.error(S("unbalanced parenthesis"));
    for (auto &g : state.grouprefpos)
        if (g.first >= (SRE_CODE)state.groups())
            throw new PatternError(new str(S("invalid group reference ") + num(g.first)), pattern, (__ss_int)g.second);

    outflags = state.flags | flags;
    compile_info(code, p, outflags, state);
    compile(code, p, outflags, state);
    code.push_back(SRE_OP_SUCCESS);
    groups = state.groups() - 1;
    groupindex = state.groupdict;
}

} // namespace __sre
} // namespace __re__
