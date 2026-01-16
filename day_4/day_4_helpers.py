# @Time    : 2026-01-13
# @Author  : Hector Astrom
# @Email   : hastrom@mit.edu
# @File    : day_4_helpers.py

from __future__ import annotations

import os
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId


# -----------------------------------------------
# MongoDB Connection Helpers
# -----------------------------------------------

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


# -----------------------------------------------
# Enum-style Literals for Validation
# -----------------------------------------------

ClassSectionType = Literal["a", "b", "c", "d", "e"]
WeekendStyleType = Literal["chill", "party", "explore", "study"]
BestWorkTimeType = Literal[1, 2, 3, 4]  # 1=morning, 2=midday, 3=evening, 4=night
HumorStyleType = Literal["dry", "quirky", "dark", "basic"]

# Valid options for multi-select fields
VALID_SPORTS = [
    "soccer", "basketball", "volleyball", "tennis", "swimming",
    "rowing", "running", "cycling", "skiing", "martial_arts", "none"
]

VALID_MUSIC_GENRES = [
    "pop", "rock", "hip_hop", "rap", "edm", "classical", "jazz",
    "r_and_b", "country", "metal", "indie", "latin", "kpop", "other"
]

VALID_HOBBIES = [
    "gaming", "reading", "cooking", "photography", "art", "music",
    "travel", "hiking", "movies", "anime", "programming", "hackathons",
    "fashion", "fitness", "social_media", "podcasts", "crafts",
    "volunteering", "languages", "writing", "none"
]

VALID_SUBJECTS = [
    "math", "physics", "chemistry", "biology", "computer_science",
    "literature", "history", "art", "music", "economics", "philosophy",
    "physical_education", "foreign_languages", "engineering", "other"
]


# -----------------------------------------------
# Nested Pydantic Models for Student Document
# -----------------------------------------------

class Demographics(BaseModel):
    """Demographic information about the student."""
    alias: str = Field(..., min_length=3, max_length=30, description="A unique alias only you will recognize")
    siblings: int = Field(..., ge=0, le=20, description="Number of siblings")
    commute_time_min: int = Field(..., gt=0, le=180, description="Commute time to school in minutes")
    class_section: ClassSectionType = Field(..., description="Class section: a, b, c, d, or e")
    hometown: str = Field(..., min_length=2, max_length=50, description="Your hometown")


class Academics(BaseModel):
    """Academic interests and preferences."""
    academic_interest: int = Field(..., ge=1, le=5, description="Academic interest level 1-5")
    favorite_subject: str = Field(..., description="Favorite subject from valid options")

    @field_validator("favorite_subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        v_lower = v.lower().strip()
        if v_lower not in VALID_SUBJECTS:
            raise ValueError(f"favorite_subject must be one of {VALID_SUBJECTS}")
        return v_lower


class Behavioral(BaseModel):
    """Behavioral and personality traits."""
    social_style: int = Field(..., ge=1, le=5, description="Social style 1-5 (introvert to extrovert)")
    weekend_style: WeekendStyleType = Field(..., description="Weekend preference: chill, party, explore, or study")
    best_work_time: BestWorkTimeType = Field(..., description="Best work time: 1=morning, 2=midday, 3=evening, 4=night")
    humor_style: HumorStyleType = Field(..., description="Humor style: dry, quirky, dark, or basic")


class Activities(BaseModel):
    """Hobbies and activities."""
    sports: List[str] = Field(..., min_length=1, description="List of sports (at least one, can be 'none')")
    music_genres: List[str] = Field(..., min_length=1, description="List of music genres")
    hobbies: List[str] = Field(..., min_length=1, description="List of hobbies")

    @field_validator("sports")
    @classmethod
    def validate_sports(cls, v: List[str]) -> List[str]:
        result = [s.lower().strip() for s in v]
        for sport in result:
            if sport not in VALID_SPORTS:
                raise ValueError(f"Invalid sport '{sport}'. Must be one of {VALID_SPORTS}")
        return result

    @field_validator("music_genres")
    @classmethod
    def validate_genres(cls, v: List[str]) -> List[str]:
        result = [g.lower().strip() for g in v]
        for genre in result:
            if genre not in VALID_MUSIC_GENRES:
                raise ValueError(f"Invalid music genre '{genre}'. Must be one of {VALID_MUSIC_GENRES}")
        return result

    @field_validator("hobbies")
    @classmethod
    def validate_hobbies(cls, v: List[str]) -> List[str]:
        result = [h.lower().strip() for h in v]
        for hobby in result:
            if hobby not in VALID_HOBBIES:
                raise ValueError(f"Invalid hobby '{hobby}'. Must be one of {VALID_HOBBIES}")
        return result


class DigitalMetrics(BaseModel):
    """Digital usage metrics."""
    avg_screen_time_min: int = Field(..., ge=0, le=1440, description="Average daily screen time in minutes")
    phone_pickups_daily: int = Field(..., ge=0, le=500, description="Average daily phone pickups")


# -----------------------------------------------
# Main Student Model
# -----------------------------------------------

class CannizzaroStudent(BaseModel):
    """
    Complete schema for a student in the ITIS Cannizzaro database.
    
    This model validates all student data before insertion into MongoDB.
    """
    demographics: Demographics
    academics: Academics
    behavioral: Behavioral
    activities: Activities
    digital_metrics: DigitalMetrics

    class Config:
        # Allow extra fields to be ignored (like _id from MongoDB)
        extra = "ignore"
