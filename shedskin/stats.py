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
import sqlite3
import tokenize
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeAlias, Optional

from . import config

if TYPE_CHECKING:
    from . import python

# types aliases
PathLike: TypeAlias = Path | str

# constanta
CREATE_DB = """\
CREATE TABLE pymodule (
    name text not null,
    filename text not null,
    n_words int default 0,
    sloc int default 0,
    prebuild_secs float default 0.0,
    build_secs float default 0.0,
    run_secs float default 0.0,

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

EXCLUDE_FIELDS = [
    "n_inherited",  # redundant with n_constraints
    "n_new_alloc_info",  # redundant with n_alloc_info
    "added_allocs",  # always 0
    "added_funcs",  # always 0
]


class ShedskinStatsManager:
    """Handles capture and persistence of shedskin-related metrics"""

    def __init__(self, gx: config.GlobalInfo, db_path: Optional[PathLike] = None):
        self.gx = gx
        self.db_path = self.get_db_path(db_path)

    @property
    def modules(self) -> list["python.Module"]:
        """Get the list of modules"""
        return [m for _, m in self.gx.modules.items() if not m.builtin]

    def get_db_path(self, db_path: Optional[PathLike] = None) -> Path:
        """Get the path to the SQLite database"""
        if not db_path:
            db_path = config.get_user_cache_dir() / "shedskin.db"
            if not db_path.parent.exists():
                db_path.parent.mkdir(parents=True)
        else:
            db_path = Path(db_path)
            if not db_path.exists():
                raise FileNotFoundError(f"Database file not found: {db_path}")
        return db_path

    def create_db(self) -> None:
        """Create the SQLite database"""
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(CREATE_DB)
            con.commit()

    def count_words(self, pyfile: Path) -> int:
        """Count the words in a Python file"""
        text = pyfile.read_text()
        return len(text.split())

    def count_lines(self, pyfile: Path) -> int:
        """Count the lines in a Python file"""
        with open(pyfile) as f:
            return len(self.compress_code(f.read()).splitlines())

    def compress_code(self, source: str) -> str:
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
            _ = tok[4]  # ltext
            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                out += " " * (start_col - last_col)
            if token_type == tokenize.COMMENT:
                pass
            elif token_type == tokenize.STRING:
                if prev_toktype != tokenize.INDENT:
                    if prev_toktype != tokenize.NEWLINE:
                        if start_col > 0:
                            if (
                                len(token_string.splitlines()) > 1
                            ):  # compress multi-line strings
                                token_string = "'<compressed>'"
                            out += token_string
            else:
                out += token_string
            prev_toktype = token_type
            last_col = end_col
            last_lineno = end_line
        out = "\n".join(line for line in out.splitlines() if line.strip())
        return out

    def name_exists(self, name: str) -> bool:
        """Check if a module name exists in the database"""
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT EXISTS(SELECT 1 FROM pymodule WHERE name = ?)", (name,))
            return cur.fetchone()[0]

    def insert_from_dict(self, table: str, entry: dict[str, Any]):
        """Insert a dictionary into a table row"""
        fields = entry.keys()
        n_fields = len(fields)
        fields_str = ", ".join(fields)
        slots = ", ".join("?" * n_fields)
        return (
            f"insert into {table} ({fields_str}) values ({slots})",
            tuple(entry.values()),
        )

    def get_stats(
        self, prebuild_secs: float, build_secs: float = 0.0, run_secs: float = 0.0
    ) -> dict[str, Any]:
        """Get partial statistics dictionary and populate with additional values"""
        _sd = self.gx.get_stats()  # partial stats from config
        _sd.update(
            dict(
                n_words=sum(self.count_words(m.filename) for m in self.modules),
                sloc=sum(self.count_lines(m.filename) for m in self.modules),
                prebuild_secs=round(prebuild_secs, 2),
                build_secs=round(build_secs, 2),
                run_secs=round(run_secs, 2),
            )
        )
        return _sd

    def insert_pymodule(
        self,
        prebuild_secs: float,
        build_secs: float = 0.0,
        run_secs: float = 0.0,
    ) -> None:
        """Insert a Python module into the database"""
        stats_dict = self.get_stats(prebuild_secs, build_secs, run_secs)
        insert, values = self.insert_from_dict("pymodule", stats_dict)
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(insert, values)

    def print_current_stats(
        self, prebuild_secs: float, build_secs: float = 0.0, run_secs: float = 0.0
    ) -> None:
        """Print current statistics of the current run."""
        stats_dict = self.get_stats(prebuild_secs, build_secs, run_secs)
        print()
        for key, value in stats_dict.items():
            if key in EXCLUDE_FIELDS:
                continue  # skip excluded fields
            if isinstance(value, bool) and not value:
                continue  # skip boolean fields that are false
            print(f"{key:>24}: {value}")
        print()

    def print_rows(self, rows: list[tuple[str, int, int, float, float, float]]) -> None:
        """Print rows of statistics"""
        max_name_len = max(len(row[0]) for row in rows)
        print(
            "NAME".ljust(max_name_len + 1),
            "WORDS".rjust(5),
            "SLOC".rjust(4),
            "STIME".rjust(5),
            "BTIME".rjust(5),
            "RTIME".rjust(5),
        )
        for name, n_words, sloc, prebuild_secs, build_secs, run_secs in rows:
            print(
                f"{name:<{max_name_len + 1}} {n_words:<5} {sloc:<4} {prebuild_secs:<5.1f} {build_secs:<5.1f} {run_secs:<5.1f}"
            )

    def print_latest_stats(self) -> None:
        """Print the statistics of the most recent run."""
        rows = self.get_latest_stats()
        self.print_rows(rows)

    def print_all_stats(self) -> None:
        """Print all statistics from the database"""
        rows = self.get_all_stats()
        self.print_rows(rows)

    def get_latest_stats(self) -> list[tuple[str, int, int, float, float, float]]:
        """Get the latest statistics from the database"""
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(
                "SELECT name, n_words, sloc, prebuild_secs, build_secs, run_secs "
                "FROM pymodule order by ran_at desc limit 1"
            )
            return cur.fetchall()

    def get_all_stats(self) -> list[tuple[str, int, int, float, float, float]]:
        """Get all statistics from the database"""
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(
                "SELECT name, n_words, sloc, prebuild_secs, build_secs, run_secs "
                "FROM pymodule order by ran_at desc"
            )
            return cur.fetchall()
