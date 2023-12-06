"""
A natural language parser for PLCFRS (probabilistic linear context-free
rewriting systems). PLCFRS is an extension of context-free grammar which
rewrites tuples of strings instead of strings; this allows it to produce
parse trees with discontinuous constituents.

Copyright 2011 Andreas van Cranenburgh <andreas@unstable.nl>
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from sys import argv, stderr
from math import exp, log
from array import array
from heapq import heappush, heappop


def parse(sent, grammar, tags, start, exhaustive):
    """parse sentence, a list of tokens, optionally with gold tags, and
    produce a chart, either exhaustive or up until the viterbi parse.
    """
    unary = grammar.unary
    lbinary = grammar.lbinary
    rbinary = grammar.rbinary
    lexical = grammar.lexical
    toid = grammar.toid
    tolabel = grammar.tolabel
    goal = ChartItem(start, (1 << len(sent)) - 1)
    maxA = 0
    blocked = 0
    Cx = [{} for _ in toid]
    C = {}
    A = agenda()

    # scan: assign part-of-speech tags
    Epsilon = toid["Epsilon"]
    for i, w in enumerate(sent):
        recognized = False
        for terminal in lexical.get(w, []):
            if not tags or tags[i] == tolabel[terminal.lhs].split("@")[0]:
                item = ChartItem(terminal.lhs, 1 << i)
                I = ChartItem(Epsilon, i)
                z = terminal.prob
                A[item] = Edge(z, z, z, I, None)
                C[item] = []
                recognized = True
        if not recognized and tags and tags[i] in toid:
            item = ChartItem(toid[tags[i]], 1 << i)
            I = ChartItem(Epsilon, i)
            A[item] = Edge(0.0, 0.0, 0.0, I, None)
            C[item] = []
            recognized = True
        elif not recognized:
            print("not covered:", tags[i] if tags else w)
            return C, None

    # parsing
    while A:
        item, edge = A.popitem()
        C[item].append(edge)
        Cx[item.label][item] = edge

        if item == goal:
            if exhaustive:
                continue
            else:
                break
        for rule in unary[item.label]:
            blocked += process_edge(
                ChartItem(rule.lhs, item.vec),
                Edge(
                    edge.inside + rule.prob,
                    edge.inside + rule.prob,
                    rule.prob,
                    item,
                    None,
                ),
                A,
                C,
                exhaustive,
            )
        for rule in lbinary[item.label]:
            for sibling in Cx[rule.rhs2]:
                e = Cx[rule.rhs2][sibling]
                if item.vec & sibling.vec == 0 and concat(rule, item.vec, sibling.vec):
                    blocked += process_edge(
                        ChartItem(rule.lhs, item.vec ^ sibling.vec),
                        Edge(
                            edge.inside + e.inside + rule.prob,
                            edge.inside + e.inside + rule.prob,
                            rule.prob,
                            item,
                            sibling,
                        ),
                        A,
                        C,
                        exhaustive,
                    )
        for rule in rbinary[item.label]:
            for sibling in Cx[rule.rhs1]:
                e = Cx[rule.rhs1][sibling]
                if sibling.vec & item.vec == 0 and concat(rule, sibling.vec, item.vec):
                    blocked += process_edge(
                        ChartItem(rule.lhs, sibling.vec ^ item.vec),
                        Edge(
                            e.inside + edge.inside + rule.prob,
                            e.inside + edge.inside + rule.prob,
                            rule.prob,
                            sibling,
                            item,
                        ),
                        A,
                        C,
                        exhaustive,
                    )
        if len(A) > maxA:
            maxA = len(A)
        # if len(A) % 10000 == 0:
        #    print "agenda max %d, now %d, items %d" % (maxA, len(A), len(C))
    stderr.write(
        "agenda max %d, now %d, items %d (%d labels), "
        % (maxA, len(A), len(C), len([_f for _f in Cx if _f]))
    )
    stderr.write("edges %d, blocked %d\n" % (sum(map(len, list(C.values()))), blocked))
    if goal not in C:
        goal = None
    return (C, goal)


def process_edge(newitem, newedge, A, C, exhaustive):
    if newitem not in C and newitem not in A:
        # prune improbable edges
        if newedge.score > 300.0:
            return 1
        # haven't seen this item before, add to agenda
        A[newitem] = newedge
        C[newitem] = []
    elif newitem in A and newedge.inside < A[newitem].inside:
        # item has lower score, update agenda
        C[newitem].append(A[newitem])
        A[newitem] = newedge
    elif exhaustive:
        # item is suboptimal, only add to exhaustive chart
        C[newitem].append(newedge)
    return 0


def concat(rule, lvec, rvec):
    lpos = nextset(lvec, 0)
    rpos = nextset(rvec, 0)
    # this algorithm was taken from rparse, FastYFComposer.
    for x in range(len(rule.args)):
        m = rule.lengths[x] - 1
        for n in range(m + 1):
            if testbit(rule.args[x], n):
                # check if there are any bits left, and
                # if any bits on the right should have gone before
                # ones on this side
                if rpos == -1 or (lpos != -1 and lpos <= rpos):
                    return False
                # jump to next gap
                rpos = nextunset(rvec, rpos)
                if lpos != -1 and lpos < rpos:
                    return False
                # there should be a gap if and only if
                # this is the last element of this argument
                if n == m:
                    if testbit(lvec, rpos):
                        return False
                elif not testbit(lvec, rpos):
                    return False
                # jump to next argument
                rpos = nextset(rvec, rpos)
            else:
                # vice versa to the above
                if lpos == -1 or (rpos != -1 and rpos <= lpos):
                    return False
                lpos = nextunset(lvec, lpos)
                if rpos != -1 and rpos < lpos:
                    return False
                if n == m:
                    if testbit(rvec, lpos):
                        return False
                elif not testbit(rvec, lpos):
                    return False
                lpos = nextset(lvec, lpos)
            # else: raise ValueError("non-binary element in yieldfunction")
    if lpos != -1 or rpos != -1:
        return False
    # everything looks all right
    return True


def mostprobablederivation(chart, start, tolabel):
    """produce a string representation of the viterbi parse in bracket
    notation"""
    edge = min(chart[start])
    return getmpd(chart, start, tolabel), edge.inside


def getmpd(chart, start, tolabel):
    edge = min(chart[start])
    if edge.right and edge.right.label:  # binary
        return "(%s %s %s)" % (
            tolabel[start.label],
            getmpd(chart, edge.left, tolabel),
            getmpd(chart, edge.right, tolabel),
        )
    else:  # unary or terminal
        return "(%s %s)" % (
            tolabel[start.label],
            getmpd(chart, edge.left, tolabel)
            if edge.left.label
            else str(edge.left.vec),
        )


def binrepr(a, sent):
    return "".join(reversed(bin(a.vec)[2:].rjust(len(sent), "0")))


def pprint_chart(chart, sent, tolabel):
    print("chart:")
    for n, a in sorted((bitcount(a.vec), a) for a in chart):
        if not chart[a]:
            continue
        print("%s[%s] =>" % (tolabel[a.label], binrepr(a, sent)))
        for edge in chart[a]:
            print("%g\t%g" % (exp(-edge.inside), exp(-edge.prob)), end=" ")
            if edge.left.label:
                print(
                    "\t%s[%s]" % (tolabel[edge.left.label], binrepr(edge.left, sent)),
                    end=" ",
                )
            else:
                print("\t", repr(sent[edge.left.vec]), end=" ")
            if edge.right:
                print(
                    "\t%s[%s]" % (tolabel[edge.right.label], binrepr(edge.right, sent)),
                    end=" ",
                )
            print()
        print()


def do(sent, grammar):
    print("sentence", sent)
    chart, start = parse(sent.split(), grammar, None, grammar.toid["S"], False)
    pprint_chart(chart, sent.split(), grammar.tolabel)
    if start:
        t, p = mostprobablederivation(chart, start, grammar.tolabel)
        print(exp(-p), t, "\n")
    else:
        print("no parse")
    return start is not None


def read_srcg_grammar(rulefile, lexiconfile):
    """Reads a grammar as produced by write_srcg_grammar."""
    srules = [line[: len(line) - 1].split("\t") for line in open(rulefile)]
    slexicon = [line[: len(line) - 1].split("\t") for line in open(lexiconfile)]
    rules = [
        (
            (
                tuple(a[: len(a) - 2]),
                tuple(tuple(map(int, b)) for b in a[len(a) - 2].split(",")),
            ),
            float(a[len(a) - 1]),
        )
        for a in srules
    ]
    lexicon = [
        ((tuple(a[: len(a) - 2]), a[len(a) - 2]), float(a[len(a) - 1]))
        for a in slexicon
    ]
    return rules, lexicon


def splitgrammar(grammar, lexicon):
    """split the grammar into various lookup tables, mapping nonterminal
    labels to numeric identifiers. Also negates log-probabilities to
    accommodate min-heaps.
    Can only represent ordered SRCG rules (monotone LCFRS)."""
    # get a list of all nonterminals; make sure Epsilon and ROOT are first,
    # and assign them unique IDs
    nonterminals = list(
        enumerate(
            ["Epsilon", "ROOT"]
            + sorted(
                set(nt for (rule, yf), weight in grammar for nt in rule)
                - set(["Epsilon", "ROOT"])
            )
        )
    )
    toid = dict((lhs, n) for n, lhs in nonterminals)
    tolabel = dict((n, lhs) for n, lhs in nonterminals)
    bylhs = [[] for _ in nonterminals]
    unary = [[] for _ in nonterminals]
    lbinary = [[] for _ in nonterminals]
    rbinary = [[] for _ in nonterminals]
    lexical = {}
    arity = array("B", [0] * len(nonterminals))
    for (tag, word), w in lexicon:
        t = Terminal(toid[tag[0]], toid[tag[1]], 0, word, abs(w))
        assert arity[t.lhs] in (0, 1)
        arity[t.lhs] = 1
        lexical.setdefault(word, []).append(t)
    for (rule, yf), w in grammar:
        args, lengths = yfarray(yf)
        assert yf == arraytoyf(args, lengths)  # unbinarized rule => error
        # cyclic unary productions
        if len(rule) == 2 and w == 0.0:
            w += 0.00000001
        r = Rule(
            toid[rule[0]],
            toid[rule[1]],
            toid[rule[2]] if len(rule) == 3 else 0,
            args,
            lengths,
            abs(w),
        )
        if arity[r.lhs] == 0:
            arity[r.lhs] = len(args)
        assert arity[r.lhs] == len(args)
        if len(rule) == 2:
            unary[r.rhs1].append(r)
            bylhs[r.lhs].append(r)
        elif len(rule) == 3:
            lbinary[r.rhs1].append(r)
            rbinary[r.rhs2].append(r)
            bylhs[r.lhs].append(r)
        else:
            raise ValueError("grammar not binarized: %r" % r)
    # assert 0 not in arity[1:]
    return Grammar(unary, lbinary, rbinary, lexical, bylhs, toid, tolabel)


def yfarray(yf):
    """convert a yield function represented as a 2D sequence to an array
    object."""
    # I for 32 bits (int), H for 16 bits (short), B for 8 bits (char)
    vectype = "I"
    vecsize = 32  # 8 * array(vectype).itemsize
    lentype = "H"
    lensize = 16  # 8 * array(lentype).itemsize
    assert len(yf) <= lensize  # arity too high?
    assert all(len(a) <= vecsize for a in yf)  # too many variables?
    initializer = [sum(1 << n for n, b in enumerate(a) if b) for a in yf]
    args = array("I", initializer)
    lengths = array("H", list(map(len, yf)))
    return args, lengths


def arraytoyf(args, lengths):
    return tuple(
        tuple(1 if a & (1 << m) else 0 for m in range(n)) for n, a in zip(lengths, args)
    )


# bit operations
def nextset(a, pos):
    """First set bit, starting from pos"""
    result = pos
    if a >> result:
        while (a >> result) & 1 == 0:
            result += 1
        return result
    return -1


def nextunset(a, pos):
    """First unset bit, starting from pos"""
    result = pos
    while (a >> result) & 1:
        result += 1
    return result


def bitcount(a):
    """Number of set bits (1s)"""
    count = 0
    while a:
        a &= a - 1
        count += 1
    return count


def testbit(a, offset):
    """Mask a particular bit, return nonzero if set"""
    return a & (1 << offset)


# various data types
class Grammar(object):
    __slots__ = ("unary", "lbinary", "rbinary", "lexical", "bylhs", "toid", "tolabel")

    def __init__(self, unary, lbinary, rbinary, lexical, bylhs, toid, tolabel):
        self.unary = unary
        self.lbinary = lbinary
        self.rbinary = rbinary
        self.lexical = lexical
        self.bylhs = bylhs
        self.toid = toid
        self.tolabel = tolabel


class ChartItem:
    __slots__ = ("label", "vec")

    def __init__(self, label, vec):
        self.label = label  # the category of this item (NP/PP/VP etc)
        self.vec = vec  # bitvector describing the spans of this item

    def __hash__(self):
        # form some reason this does not work well w/shedskin:
        # h = self.label ^ (self.vec << 31) ^ (self.vec >> 31)
        # the DJB hash function:
        h = ((5381 << 5) + 5381) * 33 ^ self.label
        h = ((h << 5) + h) * 33 ^ self.vec
        return -2 if h == -1 else h

    def __eq__(self, other):
        if other is None:
            return False
        return self.label == other.label and self.vec == other.vec

    def __lt__(self, other):
        return self.vec < other.vec


class Edge:
    __slots__ = ("score", "inside", "prob", "left", "right")

    def __init__(self, score, inside, prob, left, right):
        self.score = score
        self.inside = inside
        self.prob = prob
        self.left = left
        self.right = right

    def __lt__(self, other):
        # the ordering only depends on inside probability
        # (or on estimate of outside score when added)
        return self.score < other.score

    def __gt__(self, other):
        return self.score > other.score

    def __eq__(self, other):
        return (
            self.inside == other.inside
            and self.prob == other.prob
            and self.left == other.right
            and self.right == other.right
        )


class Terminal:
    __slots__ = ("lhs", "rhs1", "rhs2", "word", "prob")

    def __init__(self, lhs, rhs1, rhs2, word, prob):
        self.lhs = lhs
        self.rhs1 = rhs1
        self.rhs2 = rhs2
        self.word = word
        self.prob = prob


class Rule:
    __slots__ = ("lhs", "rhs1", "rhs2", "prob", "args", "lengths", "_args", "_lengths", "lengths")

    def __init__(self, lhs, rhs1, rhs2, args, lengths, prob):
        self.lhs = lhs
        self.rhs1 = rhs1
        self.rhs2 = rhs2
        self.args = args
        self.lengths = lengths
        self.prob = prob
        self._args = self.args
        self._lengths = self.lengths


# the agenda (priority queue)
class Entry(object):
    __slots__ = ("key", "value", "count")

    def __init__(self, key, value, count):
        self.key = key  # the `task'
        self.value = value  # the priority
        self.count = count  # unqiue identifier to resolve ties

    def __eq__(self, other):
        return self.count == other.count

    def __lt__(self, other):
        return self.value < other.value or (
            self.value == other.value and self.count < other.count
        )


INVALID = 0


class agenda(object):
    def __init__(self):
        self.heap = []  # the priority queue list
        self.mapping = {}  # mapping of keys to entries
        self.counter = 1  # unique sequence count

    def __setitem__(self, key, value):
        if key in self.mapping:
            oldentry = self.mapping[key]
            entry = Entry(key, value, oldentry.count)
            self.mapping[key] = entry
            heappush(self.heap, entry)
            oldentry.count = INVALID
        else:
            entry = Entry(key, value, self.counter)
            self.counter += 1
            self.mapping[key] = entry
            heappush(self.heap, entry)

    def __getitem__(self, key):
        return self.mapping[key].value

    def __contains__(self, key):
        return key in self.mapping

    def __len__(self):
        return len(self.mapping)

    def popitem(self):
        entry = heappop(self.heap)
        while entry.count is INVALID:
            entry = heappop(self.heap)
        del self.mapping[entry.key]
        return entry.key, entry.value


def batch(rulefile, lexiconfile, sentfile):
    rules, lexicon = read_srcg_grammar(rulefile, lexiconfile)
    root = rules[0][0][0][0]
    grammar = splitgrammar(rules, lexicon)
    lines = open(sentfile).read().splitlines()
    sents = [[a.split("/") for a in sent.split()] for sent in lines]
    for wordstags in sents:
        sent = [a[0] for a in wordstags]
        tags = [a[1] for a in wordstags]
        stderr.write("parsing: %s\n" % " ".join(sent))
        chart, start = parse(sent, grammar, tags, grammar.toid[root], False)
        if start:
            t, p = mostprobablederivation(chart, start, grammar.tolabel)
            print("p=%g\n%s\n\n" % (exp(-p), t))
        else:
            print("no parse\n")


def demo():
    rules = [
        ((("S", "VP2", "VMFIN"), ((0, 1, 0),)), log(1.0)),
        ((("VP2", "VP2", "VAINF"), ((0,), (0, 1))), log(0.5)),
        ((("VP2", "PROAV", "VVPP"), ((0,), (1,))), log(0.5)),
        ((("VP2", "VP2"), ((0,), (0,))), log(0.1)),
    ]
    lexicon = [
        ((("PROAV", "Epsilon"), "Darueber"), 0.0),
        ((("VAINF", "Epsilon"), "werden"), 0.0),
        ((("VMFIN", "Epsilon"), "muss"), 0.0),
        ((("VVPP", "Epsilon"), "nachgedacht"), 0.0),
    ]
    grammar = splitgrammar(rules, lexicon)

    chart, start = parse(
        "Darueber muss nachgedacht werden".split(),
        grammar,
        "PROAV VMFIN VVPP VAINF".split(),
        grammar.toid["S"],
        False,
    )
    pprint_chart(chart, "Darueber muss nachgedacht werden".split(), grammar.tolabel)
    assert mostprobablederivation(chart, start, grammar.tolabel) == (
        "(S (VP2 (VP2 (PROAV 0) (VVPP 2)) (VAINF 3)) (VMFIN 1))",
        -log(0.25),
    )
    assert do("Darueber muss nachgedacht werden", grammar)
    assert do("Darueber muss nachgedacht werden werden", grammar)
    assert do("Darueber muss nachgedacht werden werden werden", grammar)
    print("ungrammatical sentence:")
    assert not do("werden nachgedacht muss Darueber", grammar)
    print("(as expected)\n")


if __name__ == "__main__":
    if len(argv) == 4:
        batch(argv[1], argv[2], argv[3])
    else:
        demo()
        print(
            """usage: %s grammar lexicon sentences

grammar is a tab-separated text file with one rule per line, in this format:

LHS	RHS1	RHS2	YIELD-FUNC	LOGPROB
e.g., S	NP	VP	[01,10]	0.1

LHS, RHS1, and RHS2 are strings specifying the labels of this rule.
The yield function is described by a list of bit vectors such as [01,10],
where 0 is a variable that refers to a contribution by RHS1, and 1 refers to
one by RHS2. Adjacent variables are concatenated, comma-separated components
indicate discontinuities.
The final element of a rule is its log probability.
The LHS of the first rule will be used as the start symbol.

lexicon is also tab-separated, in this format:

WORD	Epsilon	TAG	LOGPROB
e.g., nachgedacht	Epsilon	VVPP	0.1

Finally, sentences is a file with one sentence per line, consisting of a space
separated list of word/tag pairs, for example:

Darueber/PROAV muss/VMFIN nachgedacht/VVPP werden/VAINF

The output consists of Viterbi parse trees where terminals have been replaced
by indices; this makes it possible to express discontinuities in otherwise
context-free trees."""
            % argv[0]
        )
