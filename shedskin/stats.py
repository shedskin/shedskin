"""shedskin.stats: project statistics.

This module provides statistics and metrics about Python code compiled with Shedskin.

Key features:
- SQLite database for storing compilation metrics
- Word and line counting utilities
- Code compression/cleaning for accurate line counts

Functions:
- get_db_path(): Get path to SQLite metrics database
- create_db(): Initialize SQLite database schema
- count_words(): Count words in a Python source file
- count_lines(): Count lines of code (excluding comments/whitespace)
- compress_code(): Clean code by removing comments and extra whitespace

"""

import io
from pathlib import Path
from textwrap import dedent
import tokenize

from typing import Any

import sqlite3

from . import config


CREATE_TABLE = """\
CREATE TABLE pymodule (
    name text not null,
    filename text not null,
    n_words int default 0,
    sloc int default 0,
    elapsed_secs float default 0.0,

    n_constraints int default 0,
    n_vars int default 0,
    n_funcs int default 0,
    n_classes int default 0,
    n_cnodes int default 0,
    n_types int default 0,
    n_orig_types int default 0,
    n_modules int default 0,
    n_templates int default 0,
    n_inheritance_relations int default 0,
    n_inheritance_temp_vars int default 0,
    n_parent_nodes int default 0,
    n_inherited int default 0,
    n_assign_target int default 0,
    n_alloc_info int default 0,
    n_new_alloc_info int default 0,
    n_iterations int default 0,
    total_iterations int default 0,
    n_called int default 0,
    added_allocs int default 0,
    added_funcs int default 0,
    cpa_limit int default 0,

    wrap_around_check bool default true,
    bounds_checking bool default true,
    assertions bool default true,
    executable_product bool default true,
    pyextension_product bool default false,
    int32 bool default false,
    int64 bool default false,
    int128 bool default false,
    float32 bool default false,
    float64 bool default false,
    silent bool default false,
    nogc bool default false,
    backtrace bool default false,

    ran_at datetime default current_timestamp
)
"""

def insert_from_dict(table: str, entry: dict[str, Any]):
    fields = entry.keys()
    n_fields = len(fields)
    fields_str = ", ".join(fields)
    slots = ", ".join("?"*n_fields)
    return (
        f"insert into {table} ({fields_str}) values ({slots})", 
        tuple(entry.values())
    )

def get_db_path() -> Path:
    """Get the path to the SQLite database"""
    return config.get_user_cache_dir() / "shedskin.db"

def create_db() -> None:
    """Create the SQLite database"""
    db_path = get_db_path()
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True)
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute(CREATE_TABLE)
        con.commit()

def count_words(pyfile: Path) -> int:
    """Count the words in a Python file"""
    text = pyfile.read_text()
    return len(text.split())

def count_lines(pyfile: Path) -> int:
    """Count the lines in a Python file"""
    with open(pyfile) as f:
        return len(compress_code(f.read()).splitlines())

def compress_code(source: str) -> str:
    """Compress the code by removing comments and unnecessary whitespace"""
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
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += (" " * (start_col - last_col))
        if token_type == tokenize.COMMENT:
            pass
        elif token_type == tokenize.STRING:
            if prev_toktype != tokenize.INDENT:
                if prev_toktype != tokenize.NEWLINE:
                    if start_col > 0:
                        if len(token_string.splitlines()) > 1:  # compress multi-line strings
                            token_string = "'<compressed>'"
                        out += token_string
        else:
            out += token_string
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
    out = '\n'.join(l for l in out.splitlines() if l.strip())
    return out

def name_exists(name: str) -> bool:
    """Check if a module name exists in the database"""
    db_path = get_db_path()
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("SELECT EXISTS(SELECT 1 FROM pymodule WHERE name = ?)", (name,))
        return cur.fetchone()[0]

def get_stats(gx: "config.globalinfo", elapsed_secs: float) -> None:
    modules = [m for _, m in gx.modules.items() if not m.builtin]
    n_words = sum(count_words(m.filename) for m in modules)
    sloc = sum(count_lines(m.filename) for m in modules)
    return gx.get_stats(n_words, sloc, elapsed_secs)

def insert_pymodule(gx: "config.globalinfo", elapsed_secs: float) -> None:
    """Insert a Python module into the database"""
    db_path = get_db_path()
    if not db_path.exists():
        create_db()
    stats_dict = get_stats(gx, elapsed_secs)
    insert, values = insert_from_dict("pymodule", stats_dict)
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute(insert, values)

def dump_current_stats(gx: "config.globalinfo", elapsed_secs: float) -> None:
    stats_dict = get_stats(gx, elapsed_secs)
    print()
    for key, value in stats_dict.items():
        print(f"{key:>24}: {value}")
    print()

def get_latest_stats() -> list[tuple[str, int, int, float]]:
    """Get the latest statistics from the database"""
    db_path = get_db_path()
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("SELECT name, n_words, sloc, round(elapsed_secs, 1) "
                    "FROM pymodule order by ran_at desc limit 1")
        return cur.fetchall()

def get_all_stats() -> list[tuple[str, int, int, float]]:
    """Get all statistics from the database"""
    db_path = get_db_path()
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("SELECT name, n_words, sloc, round(elapsed_secs, 1) "
                    "FROM pymodule order by ran_at desc")
        return cur.fetchall()

