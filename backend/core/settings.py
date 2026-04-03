from __future__ import annotations

import os
from pydantic import BaseModel


class AppSettings(BaseModel):
    app_name: str = os.getenv("PROCUREOS_APP_NAME", "ProcureOS API")
    api_prefix: str = os.getenv("PROCUREOS_API_PREFIX", "/v1")
    sqlite_path: str = os.getenv("PROCUREOS_SQLITE_PATH", "data/procureos.db")
    cors_origins: list[str] = [x.strip() for x in os.getenv("PROCUREOS_CORS_ORIGINS", "*").split(",") if x.strip()]
    rate_limit_per_minute: int = int(os.getenv("PROCUREOS_RATE_LIMIT_PER_MINUTE", "120"))


settings = AppSettings()
