#!/usr/bin/env python
"""
# from: https://stackoverflow.com/questions/1769332/script-to-remove-python-comments-docstrings
with some tweaks for rstripping
"""
import io, tokenize
import argparse


def remove_comments_and_docstrings(source):
    """
    Returns 'source' minus comments and docstrings.
    """
    io_obj = io.StringIO(source)
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        ltext = tok[4]
        # The following two conditionals preserve indentation.
        # This is necessary because we're not using tokenize.untokenize()
        # (because it spits out code with copious amounts of oddly-placed
        # whitespace).
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += " " * (start_col - last_col)
        # Remove comments:
        if token_type == tokenize.COMMENT:
            pass
        # This series of conditionals removes docstrings:
        elif token_type == tokenize.STRING:
            if prev_toktype != tokenize.INDENT:
                # This is likely a docstring; double-check we're not inside an operator:
                if prev_toktype != tokenize.NEWLINE:
                    # Note regarding NEWLINE vs NL: The tokenize module
                    # differentiates between newlines that start a new statement
                    # and newlines inside of operators such as parens, brackes,
                    # and curly braces.  Newlines inside of operators are
                    # NEWLINE and newlines that start new code are NL.
                    # Catch whole-module docstrings:
                    if start_col > 0:
                        # Unlabelled indentation means we're inside an operator
                        out += token_string
                    # Note regarding the INDENT token: The tokenize module does
                    # not label indentation inside of an operator (parens,
                    # brackets, and curly braces) as actual indentation.
                    # For example:
                    # def foo():
                    #     "The spaces before this docstring are tokenize.INDENT"
                    #     test = [
                    #         "The spaces before this string do not get a token"
                    #     ]
        else:
            out += token_string
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
    return out


def test():
    print(
        (
            remove_comments_and_docstrings(
                """\
    class fred:                              # x: [float, int]*
        def bla(self):                       # self: [fred(A)]
            self.meth_templ(1, 1)            # [int]
            self.meth_templ(1.0, 1)          # [float]

            self.hop(self.x)                 # [A]

        def meth_templ(self, x, z):          # self: [fred(A)], x: [B]r, z: [int]
            y = x                            # [B]
            return y                         # [B]

        def hop(self, x):                    # self: [fred(A)], x: [A]r
            return x                         # [A]

    a = fred()                               # [fred(int)]
    a.x = 1                                  # [int]
    a.bla()                                  # []

    b = fred()                               # [fred(float)]
    b.x = 1.0                                # [float]
    b.bla()                                  # []

    """
            )
        )
    )


def convert_files(files, rstrip=False):
    for fname in files:
        with open(fname) as f:
            source = f.read()
            cleaned = remove_comments_and_docstrings(source)
            if rstrip:
                lines = [line.rstrip() for line in cleaned.split('\n') if line != '\n']
                cleaned = "\n".join(lines)

        with open(fname, "w") as f:
            f.write(cleaned)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="rm_comments", description="removes all comments from python file(s)"
    )
    arg = opt = parser.add_argument
    arg("path", nargs="+", help="path to python file from which to remove comments")
    opt("-r", "--rstrip",  help="rstrip lines to remove residual whitespace", action="store_true")

    args = parser.parse_args()
    if args.path:
        convert_files(args.path, args.rstrip)
