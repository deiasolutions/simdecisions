-- Migration 002: Create core service tables 'tasks' and 'messages'
-- This schema is defined in ADR-006 for the Hive Control Plane.

BEGIN;

-- Tasks table to manage work for bees
CREATE TABLE IF NOT EXISTS tasks (
    id                  TEXT PRIMARY KEY, -- Using TEXT for UUIDs in SQLite
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    task_ref            TEXT NOT NULL,
    title               TEXT NOT NULL,
    description         TEXT,
    status              TEXT NOT NULL DEFAULT 'pending',
    assigned_to         TEXT,
    claimed_at          TEXT,
    completed_at        TEXT,
    outcome             TEXT,
    created_by          TEXT NOT NULL,
    priority            INTEGER DEFAULT 0,
    tags                TEXT, -- Storing as JSON array string
    file_path           TEXT,
    file_synced_at      TEXT
);

-- Messages table for bee-to-bee and human-to-bee communication
CREATE TABLE IF NOT EXISTS messages (
    id                  TEXT PRIMARY KEY, -- Using TEXT for UUIDs in SQLite
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    channel             TEXT NOT NULL,
    sender              TEXT NOT NULL,
    content             TEXT NOT NULL,
    message_type        TEXT NOT NULL DEFAULT 'text',
    reply_to            TEXT, -- Storing UUID as TEXT
    tags                TEXT, -- Storing as JSON array string
    metadata            TEXT, -- Storing JSON as TEXT
    FOREIGN KEY(reply_to) REFERENCES messages(id)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender);

COMMIT;
