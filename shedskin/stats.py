"""
Statistics about the project.
"""

import sqlite3
from textwrap import dedent
from pathlib import Path

from . import config


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
        cur.execute(dedent("""
            CREATE TABLE pymodule (
                name text not null,
                filename text not null,
                nwords int default 0,
                sloc int default 0,
                elapsed_secs float default 0.0,
                ran_at datetime default current_timestamp
            )
            """))
        con.commit()

def count_words(pyfile: Path) -> int:
    """Count the words in a Python file"""
    text = pyfile.read_text()
    return len(text.split())

def count_lines(pyfile: Path) -> int:
    """Count the lines in a Python file"""
    with open(pyfile) as f:
        lines = f.readlines()
    return len([line for line in lines if line.strip() and not line.startswith('#')])

def name_exists(name: str) -> bool:
    """Check if a module name exists in the database"""
    db_path = get_db_path()
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("SELECT EXISTS(SELECT 1 FROM pymodule WHERE name = ?)", (name,))
        return cur.fetchone()[0]

def insert_pymodule(gx: "config.globalinfo", elapsed_secs: float) -> None:
    """Insert a Python module into the database"""
    filename = gx.module_path
    pyfile = Path(filename)
    modules = [m for _, m in gx.modules.items() if not m.builtin]
    nwords = sum(count_words(m.filename) for m in modules)
    sloc = sum(count_lines(m.filename) for m in modules)
    name = pyfile.stem
    db_path = get_db_path()
    if not db_path.exists():
        create_db()
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()        
        cur.execute("INSERT INTO pymodule "
                    "(name, filename, nwords, sloc, elapsed_secs) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (name, str(filename), nwords, sloc, elapsed_secs))
        con.commit()

def get_latest_stats() -> list[tuple[str, int, int, float]]:
    """Get the latest statistics from the database"""
    db_path = get_db_path()
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("SELECT name, nwords, sloc, round(elapsed_secs, 1) "
                    "FROM pymodule order by ran_at desc limit 1")
        return cur.fetchall()


def get_all_stats() -> list[tuple[str, int, int, float]]:
    """Get all statistics from the database"""
    db_path = get_db_path()
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("SELECT name, nwords, sloc, round(elapsed_secs, 1) "
                    "FROM pymodule order by ran_at desc")
        return cur.fetchall()
