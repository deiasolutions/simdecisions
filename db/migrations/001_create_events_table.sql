-- Migration 001: Create the foundational 'events' table
-- This schema is defined in ADR-001 and includes all fields from day one
-- to ensure historical data is compatible with future features.

BEGIN;

CREATE TABLE IF NOT EXISTS events (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    event_type          TEXT NOT NULL,
    actor               TEXT NOT NULL,
    target              TEXT,
    domain              TEXT,
    signal_type         TEXT CHECK(signal_type IN ('gravity','light','internal')),
    oracle_tier         INTEGER CHECK(oracle_tier BETWEEN 0 AND 4),
    random_seed         INTEGER,
    completion_promise  TEXT,
    verification_method TEXT,
    payload_json        TEXT,
    cost_tokens         INTEGER,
    cost_usd            REAL,
    cost_carbon         REAL
);

-- Indexes to support common query patterns
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_actor ON events(actor);
CREATE INDEX IF NOT EXISTS idx_events_domain ON events(domain);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_signal ON events(signal_type);
CREATE INDEX IF NOT EXISTS idx_events_oracle ON events(oracle_tier);

COMMIT;
