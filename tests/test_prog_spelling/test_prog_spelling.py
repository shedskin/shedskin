"""Statistical spelling corrector.

After Peter Norvig's classic 21-line version (http://norvig.com/spell-correct.html),
adapted to the Shed Skin subset of Python:

- the corpus is embedded, instead of reading a 6MB 'big.txt'
- the 'known(a) or known(b) or [word]' cascade becomes explicit ifs, so that
  every branch has the same (set of str) type
- 'known' always receives a set, never a bare list
- P's 'N=sum(WORDS.values())' default argument becomes a module constant
- candidates are sorted before max(), so ties break the same way everywhere
"""

import re
from collections import Counter

CORPUS = """
The compiler reads a python module and writes a c++ module. Reading a module
is easy, writing a module is harder, and reading and writing modules quickly
is harder still. A compiler that reads python and writes c++ has to infer the
type of every expression in the module, because c++ wants a type for every
variable while python does not. Type inference is the interesting part of the
compiler, and also the slow part of the compiler. The programmer writes python,
the compiler writes c++, and the c++ compiler writes machine code, and the
machine runs the machine code very quickly indeed. Spelling a word correctly
is easier than spelling a word incorrectly, but a spelling corrector has to
handle both. The corrector reads a word, generates every word one edit away
from that word, keeps the words it knows, and returns the most probable word.
Probability comes from counting words in a corpus of text. A larger corpus
gives a better corrector, a smaller corpus gives a faster corrector, and this
corpus is very small indeed, so this corrector is very fast and not very good.
"""

WORDS = Counter(re.findall("[a-z]+", CORPUS.lower()))
TOTAL = sum(WORDS.values())

LETTERS = "abcdefghijklmnopqrstuvwxyz"


def P(word):
    """Probability of `word`."""
    return WORDS[word] / float(TOTAL)


def edits1(word):
    """All words one edit away from `word`."""
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [left + right[1:] for (left, right) in splits if right]
    transposes = [
        left + right[1] + right[0] + right[2:]
        for (left, right) in splits
        if len(right) > 1
    ]
    replaces = [
        left + c + right[1:] for (left, right) in splits if right for c in LETTERS
    ]
    inserts = [left + c + right for (left, right) in splits for c in LETTERS]
    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    """All words two edits away from `word`."""
    result = set()
    for e1 in edits1(word):
        for e2 in edits1(e1):
            result.add(e2)
    return result


def known(words):
    """The subset of `words` that appears in the corpus."""
    result = set()
    for w in words:
        if w in WORDS:
            result.add(w)
    return result


def candidates(word):
    """Possible corrections for `word`, best group first."""
    single = set()
    single.add(word)

    cands = known(single)
    if not cands:
        cands = known(edits1(word))
    if not cands:
        cands = known(edits2(word))
    if not cands:
        cands = single
    return cands


def correction(word):
    """Most probable spelling correction for `word`."""
    return max(sorted(candidates(word)), key=P)


def test_corpus():
    assert WORDS["compiler"] == 6
    assert WORDS["python"] == 4
    assert WORDS["zebra"] == 0
    assert TOTAL == 188
    assert len(WORDS) == 81
    assert 0.079 < P("the") < 0.080
    assert P("zebra") == 0.0


def test_edits1():
    # 54n + 25 candidate edits for a word of length n, minus duplicates
    assert len(edits1("a")) == 78
    assert len(edits1("ab")) == 130
    assert len(edits1("word")) == 234
    assert "wrd" in edits1("word")
    assert "owrd" in edits1("word")
    assert "ward" in edits1("word")
    assert "sword" in edits1("word")
    assert "word" in edits1("word")


def test_edits2():
    edits = edits2("ab")
    assert "ab" in edits
    assert "xaby" in edits
    assert "abcde" not in edits  # three edits away


def test_known():
    assert known(edits1("wrd")) == set(["word"])
    assert len(known(edits1("zzzz"))) == 0


def test_correction():
    # already spelled correctly
    assert correction("compiler") == "compiler"
    # one edit away
    assert correction("speling") == "spelling"
    assert correction("machne") == "machine"
    assert correction("modul") == "module"
    assert correction("qickly") == "quickly"
    # two edits away
    assert correction("korrector") == "corrector"
    assert correction("prbablity") == "probability"
    # no idea: hand the word back unchanged
    assert correction("xylophone") == "xylophone"


def test_all():
    test_corpus()
    test_edits1()
    test_edits2()
    test_known()
    test_correction()


if __name__ == "__main__":
    test_all()
