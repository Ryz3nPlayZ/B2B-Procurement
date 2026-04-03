from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from backend.core.settings import settings


def _ensure_parent(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    _ensure_parent(settings.sqlite_path)
    conn = sqlite3.connect(settings.sqlite_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def db_ready() -> bool:
    with get_conn() as conn:
        conn.execute("SELECT 1")
    return True


def init_db() -> None:
    schema_sql = """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY,
        description TEXT NOT NULL,
        applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS organizations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        plan TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        org_id TEXT NOT NULL,
        email TEXT NOT NULL,
        role TEXT NOT NULL,
        api_key_prefix TEXT NOT NULL,
        api_key_hash TEXT NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(org_id, email),
        FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS suppliers (
        id TEXT PRIMARY KEY,
        org_id TEXT NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        risk_rating REAL NOT NULL,
        preferred INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS catalog_items (
        id TEXT PRIMARY KEY,
        org_id TEXT NOT NULL,
        sku TEXT NOT NULL,
        name TEXT NOT NULL,
        unit TEXT NOT NULL,
        target_price REAL NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(org_id, sku),
        FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS rfqs (
        id TEXT PRIMARY KEY,
        org_id TEXT NOT NULL,
        item_id TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        max_budget REAL NOT NULL,
        currency TEXT NOT NULL,
        status TEXT NOT NULL,
        evaluation_strategy TEXT NOT NULL,
        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
        FOREIGN KEY (item_id) REFERENCES catalog_items(id) ON DELETE RESTRICT,
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT
    );

    CREATE TABLE IF NOT EXISTS rfq_suppliers (
        rfq_id TEXT NOT NULL,
        supplier_id TEXT NOT NULL,
        PRIMARY KEY (rfq_id, supplier_id),
        FOREIGN KEY (rfq_id) REFERENCES rfqs(id) ON DELETE CASCADE,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS bids (
        id TEXT PRIMARY KEY,
        rfq_id TEXT NOT NULL,
        supplier_id TEXT NOT NULL,
        unit_price REAL NOT NULL,
        lead_time_days INTEGER NOT NULL,
        warranty_months INTEGER NOT NULL,
        quality_score REAL NOT NULL,
        notes TEXT NOT NULL,
        submitted_at TEXT NOT NULL,
        FOREIGN KEY (rfq_id) REFERENCES rfqs(id) ON DELETE CASCADE,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS bid_scores (
        bid_id TEXT PRIMARY KEY,
        price_score REAL NOT NULL,
        quality_score REAL NOT NULL,
        delivery_score REAL NOT NULL,
        risk_score REAL NOT NULL,
        composite_score REAL NOT NULL,
        evaluated_at TEXT NOT NULL,
        FOREIGN KEY (bid_id) REFERENCES bids(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS awards (
        id TEXT PRIMARY KEY,
        rfq_id TEXT NOT NULL UNIQUE,
        winning_bid_id TEXT NOT NULL,
        awarded_by TEXT NOT NULL,
        rationale TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (rfq_id) REFERENCES rfqs(id) ON DELETE CASCADE,
        FOREIGN KEY (winning_bid_id) REFERENCES bids(id) ON DELETE RESTRICT,
        FOREIGN KEY (awarded_by) REFERENCES users(id) ON DELETE RESTRICT
    );

    CREATE INDEX IF NOT EXISTS idx_suppliers_org ON suppliers(org_id);
    CREATE INDEX IF NOT EXISTS idx_catalog_org ON catalog_items(org_id);
    CREATE INDEX IF NOT EXISTS idx_rfq_org ON rfqs(org_id);
    CREATE INDEX IF NOT EXISTS idx_bids_rfq ON bids(rfq_id);
    """
    with get_conn() as conn:
        conn.executescript(schema_sql)
        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations (version, description) VALUES (1, 'initial_enterprise_schema')"
        )
