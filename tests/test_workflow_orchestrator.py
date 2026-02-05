import unittest
import time
import os
from simdecisions.runtime.ledger import EventLedger
from simdecisions.core.workflow_orchestrator import WorkflowBuilder, WorkflowExecutor, WorkflowStatus, TaskStatus

# Simple task handlers for testing
def handler_success(context):
    time.sleep(0.1)
    return {"result": "success"}

def handler_fail(context):
    time.sleep(0.1)
    raise ValueError("This task is designed to fail")

class TestWorkflowOrchestrator(unittest.TestCase):

    def setUp(self):
        """Set up a clean event ledger for each test."""
        self.db_path = "data/test_workflow_events.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.ledger = EventLedger(db_path=self.db_path)
        self.executor = WorkflowExecutor(max_workers=2, ledger=self.ledger)

    def tearDown(self):
        """Clean up the database file after tests."""
        self.ledger.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_successful_workflow_execution_and_events(self):
        """
        Tests a workflow that should execute successfully and verifies all events are logged.
        """
        # Build workflow
        builder = WorkflowBuilder(workflow_id="wf-success", name="Successful Workflow")
        builder.add_task(task_id="task_1", name="Task 1", handler=handler_success, domain="test")
        builder.add_task(task_id="task_2", name="Task 2", handler=handler_success, domain="test", depends_on=["task_1"])
        workflow = builder.build()

        # Execute workflow
        result = self.executor.execute(workflow)

        # Assert workflow status
        self.assertEqual(result.status, WorkflowStatus.SUCCESS)

        # Assert events
        events = self.ledger.query_events(limit=100)
        event_types = [e['event_type'] for e in events]
        
        # Events are returned in descending order of time, so we check accordingly
        self.assertIn("workflow_started", event_types)
        self.assertIn("task_running", event_types)
        self.assertIn("task_succeeded", event_types)
        self.assertIn("workflow_succeeded", event_types)
        
        self.assertEqual(event_types.count("task_running"), 2)
        self.assertEqual(event_types.count("task_succeeded"), 2)

    def test_failed_workflow_execution_and_events(self):
        """
        Tests a workflow where a task fails and verifies the failure and events are logged correctly.
        """
        # Build workflow
        builder = WorkflowBuilder(workflow_id="wf-fail", name="Failed Workflow")
        builder.add_task(task_id="task_good", name="Good Task", handler=handler_success, domain="test")
        builder.add_task(task_id="task_bad", name="Bad Task", handler=handler_fail, domain="test", depends_on=["task_good"], retries=1)
        workflow = builder.build()

        # Execute workflow
        result = self.executor.execute(workflow)

        # Assert workflow status
        self.assertEqual(result.status, WorkflowStatus.FAILED)
        self.assertIn("task_bad: This task is designed to fail", result.errors)

        # Assert events
        events = self.ledger.query_events(limit=100)
        event_types = [e['event_type'] for e in events]

        self.assertIn("workflow_started", event_types)
        self.assertIn("task_running", event_types)
        self.assertIn("task_succeeded", event_types)
        self.assertIn("task_retrying", event_types)
        self.assertIn("task_failed", event_types)
        self.assertIn("workflow_failed", event_types)

        self.assertEqual(event_types.count("task_running"), 2) # task_good, task_bad
        self.assertEqual(event_types.count("task_succeeded"), 1) # only task_good
        self.assertEqual(event_types.count("task_retrying"), 1) # task_bad
        self.assertEqual(event_types.count("task_failed"), 1) # task_bad after retry

if __name__ == '__main__':
    unittest.main()
