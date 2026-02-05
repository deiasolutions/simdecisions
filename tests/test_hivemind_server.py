"""
Test script for HiveMind server functionality.
Run after starting the server: python -m deia.hivemind.runtime.server

Usage:
    python tests/test_hivemind_server.py
"""

import requests
import sys

BASE_URL = "http://localhost:8010"


def test_health():
    """Test health endpoint."""
    print("Testing /api/health...")
    resp = requests.get(f"{BASE_URL}/api/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data["status"] == "ok", f"Expected 'ok', got {data}"
    print("  [PASS] Health check passed")
    return True


def test_config():
    """Test config endpoint."""
    print("Testing /api/config...")
    resp = requests.get(f"{BASE_URL}/api/config")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert "cwd" in data, "Missing 'cwd' in config"
    assert "repo_status" in data, "Missing 'repo_status' in config"
    print(f"  [PASS] Config: cwd={data['cwd']}, status={data['repo_status']}")
    return True


def test_hive_state():
    """Test hive state endpoint."""
    print("Testing /api/hive/state...")
    resp = requests.get(f"{BASE_URL}/api/hive/state")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert "bots" in data, "Expected 'bots' in hive state"
    print(f"  [PASS] Hive state: {len(data.get('bots', []))} bots registered")
    return True


def test_channels():
    """Test channels listing."""
    print("Testing /api/channels...")
    resp = requests.get(f"{BASE_URL}/api/channels")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    # Channels returned in dict with 'channels' key
    channels = data.get("channels", data) if isinstance(data, dict) else data
    assert isinstance(channels, list), "Expected list of channels"
    print(f"  [PASS] Channels: {len(channels)} available")
    return True


def test_tasks_list():
    """Test tasks listing."""
    print("Testing /api/tasks...")
    resp = requests.get(f"{BASE_URL}/api/tasks")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    # Tasks endpoint returns dict with 'tasks' key or list
    if isinstance(data, dict):
        tasks = data.get("tasks", [])
    else:
        tasks = data
    print(f"  [PASS] Tasks: {len(tasks)} in queue")
    return True


def test_gates_status():
    """Test gates status."""
    print("Testing /api/gates...")
    resp = requests.get(f"{BASE_URL}/api/gates")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    print(f"  [PASS] Gates: {data}")
    return True


def test_activity_log():
    """Test activity log."""
    print("Testing /api/activity...")
    resp = requests.get(f"{BASE_URL}/api/activity")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    # Activity endpoint may return dict with 'entries' key or list
    if isinstance(data, dict):
        entries = data.get("entries", data.get("activities", []))
    else:
        entries = data
    print(f"  [PASS] Activity: {len(entries) if isinstance(entries, list) else 'present'}")
    return True


def test_ledger():
    """Test ledger endpoint (if exists)."""
    print("Testing /api/ledger...")
    resp = requests.get(f"{BASE_URL}/api/ledger")
    if resp.status_code == 404:
        print("  [SKIP] Ledger endpoint not implemented yet")
        return True  # Expected - TASK-009 not done
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    print(f"  [PASS] Ledger: {data}")
    return True


def main():
    print(f"\n{'='*50}")
    print("HiveMind Server Test Suite")
    print(f"Target: {BASE_URL}")
    print(f"{'='*50}\n")

    tests = [
        test_health,
        test_config,
        test_hive_state,
        test_channels,
        test_tasks_list,
        test_gates_status,
        test_activity_log,
        test_ledger,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except requests.exceptions.ConnectionError:
            print(f"  [FAIL] Connection failed - is server running?")
            print(f"\nStart server with: python -m deia.hivemind.runtime.server")
            sys.exit(1)
        except AssertionError as e:
            print(f"  [FAIL] {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
