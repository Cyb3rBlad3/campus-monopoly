from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_name: str = "CampusMonopoly API"
    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(BACKEND_ROOT / 'data' / 'campus_monopoly.db').as_posix()}",
    )
    cors_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    )


def get_settings() -> Settings:
    return Settings()
