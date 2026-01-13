# @Time    : 2026-01-13
# @Author  : Hector Astrom
# @Email   : hastrom@mit.edu
# @File    : day_3_helpers.py

from __future__ import annotations

import os
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple, Optional

import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId


# Dataset link used in the notebook
SPOTIFY_CSV_URL = (
    "https://raw.githubusercontent.com/hectorastrom/public_gtl_italy_material/refs/heads/main/day_3/spotify_dataset.csv"
)


def download_spotify_dataset(url: str, filename: str = "spotify_dataset.csv") -> str:
    """
    Download the Spotify CSV dataset to the current working directory.

    Returns the local path to the downloaded file.
    """
    if not os.path.exists(filename):
        urllib.request.urlretrieve(url, filename)
    return os.path.abspath(filename)


def load_spotify_dataframe(csv_path: str) -> pd.DataFrame:
    """
    Load the Spotify dataset CSV into a pandas DataFrame.
    """
    return pd.read_csv(csv_path)


def make_atlas_client(uri: str) -> MongoClient:
    """
    Create a MongoClient for Atlas using the stable ServerApi v1.
    """
    return MongoClient(uri, server_api=ServerApi("1"))


def ping_atlas(client: MongoClient) -> None:
    """
    Raise an exception if the Atlas connection is not healthy.
    """
    client.admin.command("ping")


def get_collections(
    client: MongoClient,
    db_name: str,
    spotify_collection_name: str = "spotify",
    playlists_collection_name: str = "playlists",
    sandbox_collection_name: str = "sandbox",
):
    """
    Return collection handles used in Day 3.
    """
    db = client[db_name]
    spotify_collection = db[spotify_collection_name]
    playlists_collection = db[playlists_collection_name]
    sandbox_collection = db[sandbox_collection_name]
    return db, spotify_collection, playlists_collection, sandbox_collection


def clear_collection(collection) -> None:
    """
    Remove all documents in a collection.
    This is intentionally simple so students can safely re-run cells.
    """
    collection.delete_many({})


def df_to_records(df: pd.DataFrame, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Convert a DataFrame into a list of Mongo-friendly dict records.

    Notes:
    - Drops NaN values (MongoDB does not want NaN).
    - Optionally limits the number of rows.
    """
    if limit is not None:
        df = df.head(int(limit))

    # Replace NaN with None, then drop keys with None values per record.
    df = df.where(pd.notnull(df), None)
    raw_records: List[Dict[str, Any]] = df.to_dict(orient="records")

    cleaned: List[Dict[str, Any]] = []
    for rec in raw_records:
        cleaned.append({k: v for k, v in rec.items() if v is not None})
    return cleaned


def objectid_to_datetime(oid: ObjectId) -> datetime:
    """
    Convert an ObjectId into a timezone-aware datetime (UTC).
    """
    # generation_time is already timezone-aware in pymongo/bson
    dt = oid.generation_time
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
