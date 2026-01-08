# @Time    : 2026-01-05 12:57
# @Author  : Hector Astrom
# @Email   : hastrom@mit.edu
# @File    : helpers.py

from typing import Any, Iterable, List
import csv
import os


def write_dicts_to_csv(
    path: str, rows: List[dict[str, Any]], fieldnames: Iterable[str] | None = None
) -> str:
    """
    Write a list of dictionaries to CSV.

    Parameters
    ----------
    path : str
        Target CSV file path.
    rows : list[dict[str, Any]]
        Rows to write; keys must align with fieldnames.
    fieldnames : iterable[str] | None
        Column order to use; defaults to keys from the first row.

    Returns
    -------
    str
        The path written, for convenience.
    """
    if not rows:
        raise ValueError("rows must contain at least one dictionary")

    resolved_fieldnames = list(fieldnames or rows[0].keys())

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=resolved_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return path