"""
Statistics about the project.
"""

import sqlite3
from pathlib import Path

from . import config

CREATE_TABLE = """
CREATE TABLE pymodule (
    name text not null,
    filename text not null,
    nwords int default 0,
    sloc int default 0,
    analysis_secs float default 0.0
)
"""


def get_db_path() -> Path:
    return config.get_user_cache_dir() / "shedskin.db"

def create_db() -> None:
    db_path = get_db_path()
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute(CREATE_TABLE)
        con.commit()

def count_words(pyfile: Path) -> int:
    text = pyfile.read_text()
    return len(text.split())

def count_lines(pyfile: Path) -> int:
    with open(pyfile) as f:
        lines = f.readlines()
    return len([line for line in lines if not line.startswith('#')]) 

def name_exists(name: str) -> bool:
    db_path = get_db_path()
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("SELECT EXISTS(SELECT 1 FROM pymodule WHERE name = ?)", (name,))
        return cur.fetchone()[0]

def insert_pymodule(filename: str, analysis_secs: float) -> None:
    pyfile = Path(filename)
    nwords = count_words(pyfile)
    sloc = count_lines(pyfile)
    name = pyfile.stem
    db_path = get_db_path()
    if not db_path.exists():
        create_db()
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()        
        cur.execute("INSERT INTO pymodule (name, filename, nwords, sloc, analysis_secs) VALUES (?, ?, ?, ?, ?)", (name, str(filename), nwords, sloc, analysis_secs))
        con.commit()

def get_pymodule_stats() -> None:
    db_path = get_db_path()
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("SELECT name, nwords, sloc, round(analysis_secs,1) FROM pymodule")
        return cur.fetchall()
