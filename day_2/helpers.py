# @Time    : 2026-01-05 12:57
# @Author  : Hector Astrom
# @Email   : hastrom@mit.edu
# @File    : helpers.py

import sqlite3
from typing import Any, List


def run_sql(cmd: str):
    """
    Executes a SQL command or a multiline SQL script, creating `temp.db` file if it doesn't exist.

    :param cmd: multiline string containing SQL command(s)
    :type cmd: str
    """
    with sqlite3.connect("temp.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(cmd)
        conn.commit()


def query_sql(cmd: str) -> List[Any]:
    """
    Query an existing SQL database.

    :param cmd: multiline string containing SQL command
    :type cmd: str
    :return: the complete result of the query
    :rtype: list[Any]
    """
    with sqlite3.connect("temp.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.execute(cmd)
        return cur.fetchall()
