"""
Tests for runtime/ledger.py - Event Ledger per ADR-001
"""
import unittest
import os
import sqlite3
import json
from runtime.ledger import EventLedger


class TestEventLedgerSchema(unittest.TestCase):
    """Test the 14-column schema per ADR-001."""

    def setUp(self):
        self.db_path = "data/test_ledger_schema.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.ledger = EventLedger(db_path=self.db_path)

    def tearDown(self):
        self.ledger.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_schema_has_14_columns(self):
        """Verify the events table has exactly 14 columns per ADR-001."""
        cursor = self.ledger.conn.cursor()
        cursor.execute("PRAGMA table_info(events)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        expected_columns = [
            'id', 'timestamp', 'event_type', 'actor', 'target', 'domain',
            'signal_type', 'oracle_tier', 'random_seed', 'completion_promise',
            'verification_method', 'payload_json', 'cost_tokens', 'cost_usd', 'cost_carbon'
        ]

        self.assertEqual(len(columns), 15)  # 14 + id
        for col in expected_columns:
            self.assertIn(col, column_names, f"Missing column: {col}")

    def test_signal_type_constraint(self):
        """Signal type must be gravity, light, or internal."""
        # Valid signal types
        for sig_type in ['gravity', 'light', 'internal']:
            event_id = self.ledger.record_event(
                event_type="test", actor="test:actor", signal_type=sig_type
            )
            self.assertIsNotNone(event_id)

        # Invalid signal type should fail
        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.record_event(
                event_type="test", actor="test:actor", signal_type="invalid"
            )

    def test_oracle_tier_constraint(self):
        """Oracle tier must be between 0 and 4."""
        # Valid tiers
        for tier in range(5):
            event_id = self.ledger.record_event(
                event_type="test", actor="test:actor", oracle_tier=tier
            )
            self.assertIsNotNone(event_id)

        # Invalid tiers should fail
        for invalid_tier in [-1, 5, 10]:
            with self.assertRaises(sqlite3.IntegrityError):
                self.ledger.record_event(
                    event_type="test", actor="test:actor", oracle_tier=invalid_tier
                )


class TestEventLedgerRecordQuery(unittest.TestCase):
    """Test record and query round-trip."""

    def setUp(self):
        self.db_path = "data/test_ledger_roundtrip.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.ledger = EventLedger(db_path=self.db_path)

    def tearDown(self):
        self.ledger.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_record_and_query_round_trip(self):
        """Record an event and query it back."""
        payload = {"key": "value", "nested": {"a": 1}}

        event_id = self.ledger.record_event(
            event_type="task_created",
            actor="agent:BEE-001",
            target="task:TASK-009",
            domain="coding",
            signal_type="gravity",
            oracle_tier=3,
            random_seed=12345,
            completion_promise="promise:abc",
            verification_method="hash",
            payload_json=payload,
            cost_tokens=100,
            cost_usd=0.002,
            cost_carbon=0.00001
        )

        self.assertIsNotNone(event_id)

        # Query it back
        events = self.ledger.query_events(event_type="task_created")
        self.assertEqual(len(events), 1)

        event = events[0]
        self.assertEqual(event['event_type'], "task_created")
        self.assertEqual(event['actor'], "agent:BEE-001")
        self.assertEqual(event['target'], "task:TASK-009")
        self.assertEqual(event['domain'], "coding")
        self.assertEqual(event['signal_type'], "gravity")
        self.assertEqual(event['oracle_tier'], 3)
        self.assertEqual(event['random_seed'], 12345)
        self.assertEqual(event['completion_promise'], "promise:abc")
        self.assertEqual(event['verification_method'], "hash")
        self.assertEqual(json.loads(event['payload_json']), payload)
        self.assertEqual(event['cost_tokens'], 100)
        self.assertAlmostEqual(event['cost_usd'], 0.002)
        self.assertAlmostEqual(event['cost_carbon'], 0.00001)

    def test_auto_timestamp(self):
        """Timestamp is auto-generated on insert."""
        event_id = self.ledger.record_event(
            event_type="test", actor="test:actor"
        )
        events = self.ledger.query_events()
        self.assertEqual(len(events), 1)
        self.assertIsNotNone(events[0]['timestamp'])
        # ISO 8601 format check
        self.assertIn('T', events[0]['timestamp'])


class TestEventLedgerFilters(unittest.TestCase):
    """Test query filters per ADR-001."""

    def setUp(self):
        self.db_path = "data/test_ledger_filters.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.ledger = EventLedger(db_path=self.db_path)

        # Seed test data
        self.ledger.record_event(event_type="task_created", actor="agent:BEE-001", domain="coding", signal_type="gravity")
        self.ledger.record_event(event_type="task_completed", actor="agent:BEE-001", domain="coding", signal_type="gravity")
        self.ledger.record_event(event_type="message_sent", actor="human:dave", domain="communication", signal_type="light")
        self.ledger.record_event(event_type="gate_checked", actor="system:minder", domain="coordination", signal_type="internal", oracle_tier=2)
        self.ledger.record_event(event_type="flight_started", actor="system:minder", domain="coordination", signal_type="gravity", oracle_tier=3)

    def tearDown(self):
        self.ledger.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_filter_by_event_type(self):
        events = self.ledger.query_events(event_type="task_created")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['event_type'], "task_created")

    def test_filter_by_actor(self):
        events = self.ledger.query_events(actor="agent:BEE-001")
        self.assertEqual(len(events), 2)
        for e in events:
            self.assertEqual(e['actor'], "agent:BEE-001")

    def test_filter_by_domain(self):
        events = self.ledger.query_events(domain="coordination")
        self.assertEqual(len(events), 2)
        for e in events:
            self.assertEqual(e['domain'], "coordination")

    def test_filter_by_signal_type(self):
        events = self.ledger.query_events(signal_type="light")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['signal_type'], "light")

    def test_filter_by_oracle_tier(self):
        events = self.ledger.query_events(oracle_tier=3)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['oracle_tier'], 3)

    def test_combined_filters(self):
        events = self.ledger.query_events(actor="system:minder", signal_type="gravity")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['event_type'], "flight_started")

    def test_pagination(self):
        # Get all 5 events
        all_events = self.ledger.query_events(limit=100)
        self.assertEqual(len(all_events), 5)

        # Paginate
        page1 = self.ledger.query_events(limit=2, offset=0)
        page2 = self.ledger.query_events(limit=2, offset=2)
        page3 = self.ledger.query_events(limit=2, offset=4)

        self.assertEqual(len(page1), 2)
        self.assertEqual(len(page2), 2)
        self.assertEqual(len(page3), 1)


class TestEventLedgerAppendOnly(unittest.TestCase):
    """Test append-only enforcement per ADR-001."""

    def setUp(self):
        self.db_path = "data/test_ledger_append_only.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.ledger = EventLedger(db_path=self.db_path)
        self.ledger.record_event(event_type="test", actor="test:actor")

    def tearDown(self):
        self.ledger.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_update_blocked(self):
        """UPDATE operations should be blocked."""
        cursor = self.ledger.conn.cursor()
        with self.assertRaises(sqlite3.IntegrityError) as ctx:
            cursor.execute("UPDATE events SET event_type = 'modified' WHERE id = 1")
        self.assertIn("append-only", str(ctx.exception).lower())

    def test_delete_blocked(self):
        """DELETE operations should be blocked."""
        cursor = self.ledger.conn.cursor()
        with self.assertRaises(sqlite3.IntegrityError) as ctx:
            cursor.execute("DELETE FROM events WHERE id = 1")
        self.assertIn("append-only", str(ctx.exception).lower())

    def test_insert_allowed(self):
        """INSERT operations should still work."""
        event_id = self.ledger.record_event(event_type="another", actor="test:actor")
        self.assertIsNotNone(event_id)
        events = self.ledger.query_events()
        self.assertEqual(len(events), 2)


class TestUniversalEntityIds(unittest.TestCase):
    """Test universal entity ID convention per ADR-003."""

    def setUp(self):
        self.db_path = "data/test_ledger_entity_ids.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.ledger = EventLedger(db_path=self.db_path)

    def tearDown(self):
        self.ledger.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_entity_id_formats(self):
        """Verify various entity ID formats work correctly."""
        test_cases = [
            ("human:dave", "task:TASK-009"),
            ("agent:BEE-001", "task:TASK-010"),
            ("system:minder", "flight:FLIGHT-001"),
            ("bot:codex-001", "decision:DEC-001"),
        ]

        for actor, target in test_cases:
            event_id = self.ledger.record_event(
                event_type="test", actor=actor, target=target
            )
            self.assertIsNotNone(event_id)

        # Query back and verify
        events = self.ledger.query_events(actor="human:dave")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['target'], "task:TASK-009")


if __name__ == '__main__':
    unittest.main()
