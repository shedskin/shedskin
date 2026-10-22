# Copies the game of tpy-another-world (https://github.com/trozen/tpy-another-world)
# here, as another_world/ and aw.py, rewritten for Shedskin:
#   - variable annotations dropped, declarations without a value kept as
#     comments; function signatures kept (Shedskin ignores them), with TPy's
#     fixed-width ints as int, Own[T] as T and types.FrameType as object;
#     --no-signatures drops those too
#   - `from tpy/typing/types import ...` dropped
#   - int8(x) .. uint64(x) -> int(x)
#   - main.py: the argparse parser is replaced by another_world/cmdline.py,
#     generated here from the same parser (run under CPython): a class with
#     a typed field per argument, parsed with getopt.gnu_getopt, with
#     argparse's help, usage and error messages
#   - audio.py: poll() results are tested against subprocess.NO_STATUS
#     instead of None (see subprocess.py, which is not generated)
# Usage: python3 prep.py [--no-signatures] GAME_REPO
import argparse
import ast
import os
import shutil
import sys

SIGNATURES = "--no-signatures" not in sys.argv
(SRC,) = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = os.path.dirname(os.path.abspath(__file__))
FIXED = {"int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64"}
DROP_IMPORTS = {"tpy", "typing", "types"}


class Annotation(ast.NodeTransformer):
    """A signature annotation, in plain Python types."""

    def visit_Name(self, node):
        if node.id in FIXED:
            node.id = "int"
        elif node.id == "FrameType":
            node.id = "object"
        return node

    def visit_Subscript(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Name) and node.value.id == "Own":
            return node.slice
        return node

    def visit_Constant(self, node):
        if isinstance(node.value, str):  # a quoted annotation
            tree = ast.parse(node.value, mode="eval")
            node.value = ast.unparse(self.visit(tree.body))
        return node


class Source:
    """Edits of a source text at AST positions (in UTF-8 bytes), so the rest
    stays as it is, comments included."""

    def __init__(self, text):
        self.data = text.encode()
        self.starts = [0]
        for line in self.data.split(b"\n"):
            self.starts.append(self.starts[-1] + len(line) + 1)
        self.edits = []

    def offset(self, line, col):
        return self.starts[line - 1] + col

    def replace(self, start, end, text):
        self.edits.append((start, end, text.encode()))

    def node(self, node, text):
        self.replace(self.offset(node.lineno, node.col_offset),
                     self.offset(node.end_lineno, node.end_col_offset), text)

    def lines(self, node):
        """Removes the lines of a statement, and a blank line after them
        if one comes before them too."""
        end = self.starts[node.end_lineno]
        if (node.lineno > 1 and self.line(node.lineno - 1) == b""
                and node.end_lineno < len(self.starts) - 1 and self.line(node.end_lineno + 1) == b""):
            end = self.starts[node.end_lineno + 1]
        self.replace(self.starts[node.lineno - 1], end, "")

    def line(self, n):
        return self.data[self.starts[n - 1]:self.starts[n] - 1].strip()

    def text(self):
        data = self.data
        for start, end, text in sorted(self.edits, reverse=True):
            data = data[:start] + text + data[end:]
        return data.decode()


def lower(tree, src):
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in DROP_IMPORTS:
            src.lines(node)
        elif isinstance(node, ast.AnnAssign):
            if node.value is None:  # a declaration only, kept as a comment
                src.node(node, "# %s: %s" % (ast.unparse(node.target),
                                             ast.unparse(Annotation().visit(node.annotation))))
            else:
                src.replace(src.offset(node.target.end_lineno, node.target.end_col_offset),
                            src.offset(node.value.lineno, node.value.col_offset), " = ")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a = node.args
            for arg in a.posonlyargs + a.args + a.kwonlyargs + [a.vararg, a.kwarg]:
                if arg is not None and arg.annotation is not None:
                    if SIGNATURES:
                        src.node(arg.annotation, ast.unparse(Annotation().visit(arg.annotation)))
                    else:
                        src.replace(src.offset(arg.lineno, arg.col_offset + len(arg.arg)),
                                    src.offset(arg.annotation.end_lineno, arg.annotation.end_col_offset), "")
            if node.returns is not None:
                if SIGNATURES:
                    src.node(node.returns, ast.unparse(Annotation().visit(node.returns)))
                else:  # from the ')' before '->'
                    line = src.data[:src.offset(node.returns.lineno, node.returns.col_offset)]
                    src.replace(line.rindex(b")") + 1,
                                src.offset(node.returns.end_lineno, node.returns.end_col_offset), "")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FIXED:
            src.node(node.func, "int")


def is_parser_call(stmt, method):
    return (isinstance(stmt, (ast.Expr, ast.Assign)) and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Attribute) and stmt.value.func.attr == method
            and isinstance(stmt.value.func.value, ast.Name) and stmt.value.func.value.id == "parser")


def replace_argparse(tree, src):
    """Takes the parser statements out of main(), builds the parser under
    CPython, and returns the source of cmdline.py."""
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    building = []
    for stmt in main.body:
        if (isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "ArgumentParser"):
            building.append(stmt)
            src.lines(stmt)
        elif is_parser_call(stmt, "add_argument"):
            building.append(stmt)
            src.lines(stmt)
        elif is_parser_call(stmt, "parse_args"):
            src.node(stmt.value.func, "parse_args")
    for node in tree.body:
        if isinstance(node, ast.Import) and node.names[0].name == "argparse":
            src.lines(node)
        elif isinstance(node, ast.ImportFrom) and node.module == "argparse":
            src.lines(node)
        elif isinstance(node, ast.ImportFrom) and node.module == "clock":
            src.replace(src.starts[node.end_lineno], src.starts[node.end_lineno],
                        "from .cmdline import parse_args\n")

    env = {"argparse": argparse, "ArgumentParser": argparse.ArgumentParser}
    exec(compile(ast.fix_missing_locations(ast.Module(building, [])), "main.py", "exec"), env)
    parser = env["parser"]
    os.environ["COLUMNS"] = "80"
    return gen_cmdline(parser)


def gen_cmdline(parser):
    usage = parser.format_usage()
    help_text = parser.format_help()
    shorts = ""
    longs = []
    fields = []      # (dest, default literal)
    handlers = []    # code per option
    positionals = []
    for action in parser._actions:
        if isinstance(action, argparse._HelpAction):
            shorts += "h"
            longs.append("help")
            continue
        if not action.option_strings:
            positionals.append(action)
            fields.append((action.dest, "''"))
            continue
        flag = isinstance(action, argparse._StoreTrueAction)
        assert flag or type(action) is argparse._StoreAction, action
        name = "/".join(action.option_strings)
        for opt in action.option_strings:
            if opt.startswith("--"):
                longs.append(opt[2:] + ("" if flag else "="))
            else:
                shorts += opt[1:] + ("" if flag else ":")
        test = " or ".join("opt == %r" % o for o in action.option_strings)
        if flag:
            fields.append((action.dest, "False"))
            handlers.append("        elif %s:\n            args.%s = True\n" % (test, action.dest))
            continue
        assert action.type in (None, int), action
        default = action.default if action.default is not None else ("" if action.type is None else 0)
        fields.append((action.dest, repr(default)))
        value = "_int(%r, value)" % name if action.type is int else "value"
        code = "        elif %s:\n            args.%s = %s\n" % (test, action.dest, value)
        if action.choices:
            code += ("            if args.%s not in %r:\n"
                     "                _fail('argument %s: invalid choice: ' + repr(args.%s) + %r)\n"
                     % (action.dest, list(action.choices), name, action.dest,
                        " (choose from %s)" % ", ".join(repr(c) for c in action.choices)))
        handlers.append(code)
    names = " ".join(p.metavar or p.dest for p in positionals)
    out = ['''# Generated by prep.py from the game's argparse parser: the same options,
# parsed with getopt, with argparse's help, usage and error messages.
import getopt
import sys

USAGE = %r

HELP = %r


class Args:
    def __init__(self):
''' % (usage, help_text)]
    for dest, default in fields:
        out.append("        self.%s = %s\n" % (dest, default))
    out.append('''

def _fail(message):
    sys.stderr.write(USAGE)
    sys.stderr.write(%r + message + '\\n')
    sys.exit(2)


def _int(name, value):
    try:
        return int(value)
    except ValueError:
        _fail('argument ' + name + ': invalid int value: ' + repr(value))
    return 0


def _name(opt):
    for names in %r:
        if opt in names.split('/'):
            return names
    return opt


def parse_args(argv):
    args = Args()
    try:
        opts, rest = getopt.gnu_getopt(argv, %r, %r)
    except getopt.GetoptError as e:
        opt = e.msg.split(' ')[1]  # 'option --x not recognized', 'option -x requires argument'
        if e.msg.endswith('requires argument'):
            _fail('argument ' + _name(opt) + ': expected one argument')
        _fail('unrecognized arguments: ' + opt)
        return args
    for opt, value in opts:
        if opt == '-h' or opt == '--help':
            sys.stdout.write(HELP)
            sys.exit(0)
''' % ("%s: error: " % parser.prog,
       ["/".join(a.option_strings) for a in parser._actions if a.option_strings],
       shorts, longs))
    out.extend(handlers)
    out.append('''    if len(rest) < %d:
        _fail('the following arguments are required: %s')
    if len(rest) > %d:
        _fail('unrecognized arguments: ' + ' '.join(rest[%d:]))
''' % (len(positionals), ", ".join(p.metavar or p.dest for p in positionals),
       len(positionals), len(positionals)))
    for i, p in enumerate(positionals):
        out.append("    args.%s = rest[%d]\n" % (p.dest, i))
    out.append("    return args\n")
    return "".join(out).replace("\n        elif", "\n        if", 1)


def patch(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new)


if os.path.isdir(os.path.join(OUT, "another_world")):
    shutil.rmtree(os.path.join(OUT, "another_world"))
for root, dirs, files in os.walk(os.path.join(SRC, "another_world")):
    for f in files:
        if not f.endswith(".py"):
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, SRC)
        source = open(path).read()
        if rel == os.path.join("another_world", "audio.py"):
            source = patch(source, "player.poll() is not None", "player.poll() != NO_STATUS")
            source = patch(source, "if code is None:", "if code == NO_STATUS:")
            source = patch(source, "from subprocess import DEVNULL, PIPE, Popen",
                           "from subprocess import DEVNULL, NO_STATUS, PIPE, Popen")
        tree = ast.parse(source, path)
        src = Source(source)
        if rel == os.path.join("another_world", "main.py"):
            cmdline = replace_argparse(tree, src)
            os.makedirs(os.path.join(OUT, "another_world"), exist_ok=True)
            with open(os.path.join(OUT, "another_world", "cmdline.py"), "w") as out:
                out.write(cmdline)
        lower(tree, src)
        text = src.text()
        ast.parse(text, path)
        dest = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as out:
            out.write(text)
shutil.copy(os.path.join(SRC, "aw.py"), OUT)
