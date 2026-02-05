import sqlite3
import json
import os
import threading

class EventLedger:
    def __init__(self, db_path='data/events.db'):
        self.db_path = db_path
        self._ensure_data_directory_exists()
        self._local = threading.local()
        # Initial table creation from the main thread
        self._create_table()

    @property
    def conn(self):
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _ensure_data_directory_exists(self):
        dirname = os.path.dirname(self.db_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
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
            )
        """)
        # Create indexes as defined in ADR-001
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_actor ON events(actor)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_domain ON events(domain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_signal ON events(signal_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_oracle ON events(oracle_tier)")

        # Append-only enforcement: triggers to prevent UPDATE and DELETE (ADR-001)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS prevent_update_events
            BEFORE UPDATE ON events
            BEGIN
                SELECT RAISE(ABORT, 'Event ledger is append-only: UPDATE not allowed');
            END
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS prevent_delete_events
            BEFORE DELETE ON events
            BEGIN
                SELECT RAISE(ABORT, 'Event ledger is append-only: DELETE not allowed');
            END
        """)
        self.conn.commit()

    def record_event(self, event_type: str, actor: str, target: str = None, domain: str = None,
                     signal_type: str = None, oracle_tier: int = None, random_seed: int = None,
                     completion_promise: str = None, verification_method: str = None,
                     payload_json: dict = None, cost_tokens: int = None, cost_usd: float = None,
                     cost_carbon: float = None):
        
        # Ensure payload_json is a string if not None
        if payload_json is not None and isinstance(payload_json, dict):
            payload_json = json.dumps(payload_json)

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO events (
                event_type, actor, target, domain, signal_type, oracle_tier,
                random_seed, completion_promise, verification_method, payload_json,
                cost_tokens, cost_usd, cost_carbon
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_type, actor, target, domain, signal_type, oracle_tier,
                random_seed, completion_promise, verification_method, payload_json,
                cost_tokens, cost_usd, cost_carbon
            )
        )
        self.conn.commit()
        return cursor.lastrowid

    def query_events(self, event_type: str = None, actor: str = None, target: str = None,
                     domain: str = None, signal_type: str = None, oracle_tier: int = None,
                     start_timestamp: str = None, end_timestamp: str = None,
                     limit: int = 100, offset: int = 0):
        
        query = "SELECT * FROM events WHERE 1=1"
        params = []

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if actor:
            query += " AND actor = ?"
            params.append(actor)
        if target:
            query += " AND target = ?"
            params.append(target)
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        if signal_type:
            query += " AND signal_type = ?"
            params.append(signal_type)
        if oracle_tier is not None:
            query += " AND oracle_tier = ?"
            params.append(oracle_tier)
        if start_timestamp:
            query += " AND timestamp >= ?"
            params.append(start_timestamp)
        if end_timestamp:
            query += " AND timestamp <= ?"
            params.append(end_timestamp)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        if hasattr(self._local, 'conn') and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None

if __name__ == '__main__':
    # Example Usage:
    ledger = EventLedger(db_path='data/test_events.db')

    # Record some events
    event_id1 = ledger.record_event(
        event_type="task_created",
        actor="agent:Q33N-001",
        target="task:TASK-009",
        domain="coding",
        signal_type="gravity",
        payload_json={"description": "Initial ledger implementation"}
    )
    print(f"Recorded event 1 with ID: {event_id1}")

    event_id2 = ledger.record_event(
        event_type="message_sent",
        actor="human:dave",
        target="agent:Q33N-001",
        domain="communication",
        signal_type="light",
        payload_json={"message": "Assume role of Q33N"},
        cost_tokens=50,
        cost_usd=0.001
    )
    print(f"Recorded event 2 with ID: {event_id2}")

    event_id3 = ledger.record_event(
        event_type="flight_started",
        actor="system:minder",
        domain="coordination",
        oracle_tier=3,
        payload_json={"flight_id": "FLIGHT-001"}
    )
    print(f"Recorded event 3 with ID: {event_id3}")
    
    event_id4 = ledger.record_event(
        event_type="task_completed",
        actor="agent:Q33N-001",
        target="task:TASK-009",
        domain="coding",
        signal_type="gravity",
        oracle_tier=3,
        cost_tokens=1000,
        cost_usd=0.02,
        cost_carbon=0.00001 # Example value
    )
    print(f"Recorded event 4 with ID: {event_id4}")

    # Query events
    all_events = ledger.query_events()
    print("\nAll events:")
    for event in all_events:
        print(event)

    coding_events = ledger.query_events(domain="coding")
    print("\nCoding events:")
    for event in coding_events:
        print(event)
    
    q33n_events = ledger.query_events(actor="agent:Q33N-001")
    print("\nQ33N events:")
    for event in q33n_events:
        print(event)

    ledger.close()
    print("\nEventLedger closed.")
