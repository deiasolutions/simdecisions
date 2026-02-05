"""
Workflow Orchestration Engine - DAG-based workflow execution with branching, error handling, parallelism.

Defines and executes multi-step workflows with dependencies, conditional branching,
error handling/retries, state management, monitoring, and parallel execution.
"""

from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import threading
from datetime import datetime, timedelta
import logging
import json
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..runtime.ledger import EventLedger

logger = logging.getLogger(__name__)


# ===== ENUMS =====

class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    CREATED = "created"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BranchCondition(str, Enum):
    """Branch conditions."""
    IF_SUCCESS = "if_success"
    IF_FAILED = "if_failed"
    IF_SKIPPED = "if_skipped"
    ALWAYS = "always"


# ===== DATA STRUCTURES =====

@dataclass
class TaskDefinition:
    """Definition of a single task in workflow."""
    task_id: str
    name: str
    handler: Callable[[Dict[str, Any]], Any]
    domain: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    retries: int = 0
    timeout: Optional[float] = None
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecution:
    """Execution record for a task."""
    task_id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    attempts: int = 0
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """Get execution duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""
    workflow_id: str
    name: str
    description: str = ""
    tasks: Dict[str, TaskDefinition] = field(default_factory=dict)
    start_task: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Execution record for a workflow."""
    workflow_id: str
    execution_id: str
    name: str
    status: WorkflowStatus = WorkflowStatus.CREATED
    tasks: Dict[str, TaskExecution] = field(default_factory=dict)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """Get total duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    @property
    def is_complete(self) -> bool:
        """Check if workflow is complete."""
        return self.status in [WorkflowStatus.SUCCESS, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]


# ===== WORKFLOW BUILDER =====

class WorkflowBuilder:
    """Build workflows fluently."""

    def __init__(self, workflow_id: str = None, name: str = ""):
        """Initialize builder."""
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.name = name
        self.description = ""
        self.tasks: Dict[str, TaskDefinition] = {}
        self.start_task = None

    def with_description(self, description: str) -> "WorkflowBuilder":
        """Add description."""
        self.description = description
        return self

    def add_task(self, task_id: str, name: str, handler: Callable, domain: Optional[str] = None, depends_on: List[str] = None,
                 retries: int = 0, timeout: Optional[float] = None,
                 condition: Optional[Callable] = None) -> "WorkflowBuilder":
        """Add task to workflow."""
        self.tasks[task_id] = TaskDefinition(
            task_id=task_id,
            name=name,
            handler=handler,
            domain=domain,
            depends_on=depends_on or [],
            retries=retries,
            timeout=timeout,
            condition=condition
        )

        if self.start_task is None:
            self.start_task = task_id

        return self

    def set_start_task(self, task_id: str) -> "WorkflowBuilder":
        """Set starting task."""
        self.start_task = task_id
        return self

    def build(self) -> WorkflowDefinition:
        """Build workflow."""
        return WorkflowDefinition(
            workflow_id=self.workflow_id,
            name=self.name,
            description=self.description,
            tasks=self.tasks,
            start_task=self.start_task
        )


# ===== EXECUTION ENGINE =====

class WorkflowExecutor:
    """Execute workflows with state management."""

    def __init__(self, max_workers: int = 4, ledger: Optional[EventLedger] = None):
        """Initialize executor."""
        self.max_workers = max_workers
        self.lock = threading.RLock()
        self.executions: Dict[str, WorkflowExecution] = {}
        self.ledger = ledger

    def execute(self, workflow: WorkflowDefinition) -> WorkflowExecution:
        """Execute workflow."""
        execution = WorkflowExecution(
            workflow_id=workflow.workflow_id,
            execution_id=str(uuid.uuid4()),
            name=workflow.name
        )

        if self.ledger:
            self.ledger.record_event(
                event_type="workflow_started",
                actor="system:workflow_executor",
                target=execution.execution_id,
                domain="system",
                payload_json={"workflow_name": workflow.name, "workflow_id": workflow.workflow_id}
            )

        with self.lock:
            self.executions[execution.execution_id] = execution

        execution.start_time = time.time()
        execution.status = WorkflowStatus.RUNNING

        try:
            self._execute_tasks(workflow, execution)

            if any(t.status == TaskStatus.FAILED for t in execution.tasks.values()):
                execution.status = WorkflowStatus.FAILED
                if self.ledger:
                    self.ledger.record_event(
                        event_type="workflow_failed",
                        actor="system:workflow_executor",
                        target=execution.execution_id,
                        domain="system",
                        payload_json={"errors": execution.errors}
                    )
            else:
                execution.status = WorkflowStatus.SUCCESS
                if self.ledger:
                    self.ledger.record_event(
                        event_type="workflow_succeeded",
                        actor="system:workflow_executor",
                        target=execution.execution_id,
                        domain="system"
                    )

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.errors.append(str(e))
            if self.ledger:
                self.ledger.record_event(
                    event_type="workflow_failed",
                    actor="system:workflow_executor",
                    target=execution.execution_id,
                    domain="system",
                    payload_json={"error": str(e)}
                )

        execution.end_time = time.time()
        return execution

    def _execute_tasks(self, workflow: WorkflowDefinition, execution: WorkflowExecution) -> None:
        """Execute tasks with dependency ordering."""
        from concurrent.futures import wait, FIRST_COMPLETED

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            task_defs = workflow.tasks

            # Build dependency graph
            downstream_map = {task_id: [] for task_id in task_defs}
            dependency_count = {task_id: len(task_def.depends_on) for task_id, task_def in task_defs.items()}
            for task_id, task_def in task_defs.items():
                for dep in task_def.depends_on:
                    downstream_map[dep].append(task_id)

            submitted_tasks = set()

            while len(execution.tasks) < len(task_defs):
                # Find and submit ready tasks
                ready_to_submit = False
                for task_id, count in dependency_count.items():
                    if count == 0 and task_id not in submitted_tasks:
                        task_def = task_defs[task_id]
                        task_exec = TaskExecution(task_id=task_id, name=task_def.name)
                        execution.tasks[task_id] = task_exec
                        future = executor.submit(self._execute_task, task_def, task_exec, execution)
                        futures[future] = task_id
                        submitted_tasks.add(task_id)
                        ready_to_submit = True
                
                # If no tasks are ready and none are running, there might be a cycle or failure
                if not ready_to_submit and not futures:
                    break

                # Wait for at least one task to complete
                done, _ = wait(futures, return_when=FIRST_COMPLETED)

                for future in done:
                    completed_task_id = futures.pop(future)
                    
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Task {completed_task_id} failed with exception: {e}")

                    task_exec = execution.tasks[completed_task_id]
                    if task_exec.status == TaskStatus.SUCCESS:
                        for downstream_task_id in downstream_map[completed_task_id]:
                            dependency_count[downstream_task_id] -= 1
                    elif task_exec.status == TaskStatus.FAILED:
                        # If a task fails, we should not execute its downstream tasks.
                        # We can mark them as skipped.
                        # This part can be enhanced later. For now, we just don't decrement the count.
                        pass

    def _execute_task(self, task_def: TaskDefinition, task_exec: TaskExecution,
                      execution: WorkflowExecution) -> None:
        """Execute single task with retry logic."""
        if self.ledger:
            self.ledger.record_event(
                event_type="task_running",
                actor="system:workflow_executor",
                target=task_def.task_id,
                domain=task_def.domain,
                payload_json={"workflow_id": execution.workflow_id, "execution_id": execution.execution_id}
            )
        task_exec.status = TaskStatus.RUNNING
        task_exec.start_time = time.time()

        for attempt in range(task_def.retries + 1):
            try:
                task_exec.attempts = attempt + 1

                if task_def.condition:
                    if not task_def.condition(execution.outputs):
                        if self.ledger:
                            self.ledger.record_event(
                                event_type="task_skipped",
                                actor="system:workflow_executor",
                                target=task_def.task_id,
                                domain=task_def.domain,
                                payload_json={"condition": "failed"}
                            )
                        task_exec.status = TaskStatus.SKIPPED
                        task_exec.end_time = time.time()
                        return

                # Get dependencies outputs
                context = {dep: execution.tasks[dep].result for dep in task_def.depends_on}

                # Execute with timeout
                if task_def.timeout:
                    import signal

                    def timeout_handler(signum, frame):
                        raise TimeoutError(f"Task {task_def.task_id} timeout")

                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(int(task_def.timeout))

                result = task_def.handler(context)

                if task_def.timeout:
                    signal.alarm(0)

                task_exec.result = result
                task_exec.status = TaskStatus.SUCCESS
                execution.outputs[task_def.task_id] = result
                if self.ledger:
                     self.ledger.record_event(
                        event_type="task_succeeded",
                        actor="system:workflow_executor",
                        target=task_def.task_id,
                        domain=task_def.domain,
                        payload_json={"result": str(result)} # Convert result to string for logging
                    )

                task_exec.end_time = time.time()
                return

            except Exception as e:
                if attempt < task_def.retries:
                    if self.ledger:
                        self.ledger.record_event(
                            event_type="task_retrying",
                            actor="system:workflow_executor",
                            target=task_def.task_id,
                            domain=task_def.domain,
                            payload_json={"attempt": attempt + 1, "error": str(e)}
                        )
                    task_exec.status = TaskStatus.RETRYING
                    time.sleep(1)  # Backoff
                else:
                    if self.ledger:
                        self.ledger.record_event(
                            event_type="task_failed",
                            actor="system:workflow_executor",
                            target=task_def.task_id,
                            domain=task_def.domain,
                            payload_json={"error": str(e)}
                        )
                    task_exec.status = TaskStatus.FAILED
                    task_exec.error = str(e)
                    execution.errors.append(f"{task_def.task_id}: {str(e)}")
                    task_exec.end_time = time.time()
                    return


# ===== STATE MANAGEMENT =====

class WorkflowState:
    """Manage workflow state persistence."""

    def __init__(self):
        """Initialize state manager."""
        self.state: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()

    def save_state(self, execution_id: str, state: Dict[str, Any]) -> None:
        """Save execution state."""
        with self.lock:
            self.state[execution_id] = state.copy()

    def get_state(self, execution_id: str) -> Dict[str, Any]:
        """Get execution state."""
        with self.lock:
            return self.state.get(execution_id, {}).copy()

    def to_json(self, execution: WorkflowExecution) -> str:
        """Serialize execution to JSON."""
        data = {
            "workflow_id": execution.workflow_id,
            "execution_id": execution.execution_id,
            "name": execution.name,
            "status": execution.status.value,
            "duration": execution.duration,
            "tasks": {
                task_id: {
                    "status": task.status.value,
                    "duration": task.duration,
                    "attempts": task.attempts,
                    "error": task.error
                }
                for task_id, task in execution.tasks.items()
            }
        }
        return json.dumps(data, indent=2)


# ===== MONITORING =====

class WorkflowMonitor:
    """Monitor workflow execution."""

    def __init__(self):
        """Initialize monitor."""
        self.executions: List[WorkflowExecution] = []
        self.lock = threading.RLock()

    def record_execution(self, execution: WorkflowExecution) -> None:
        """Record completed execution."""
        with self.lock:
            self.executions.append(execution)

    def get_success_rate(self) -> float:
        """Get success rate."""
        with self.lock:
            if not self.executions:
                return 0.0
            successful = sum(1 for e in self.executions if e.status == WorkflowStatus.SUCCESS)
            return successful / len(self.executions)

    def get_average_duration(self) -> float:
        """Get average execution duration."""
        with self.lock:
            if not self.executions:
                return 0.0
            total_duration = sum(e.duration for e in self.executions if e.duration)
            return total_duration / len(self.executions)

    def get_task_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get task-level statistics."""
        stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "executions": 0, "successes": 0, "failures": 0, "avg_duration": 0.0
        })

        with self.lock:
            for execution in self.executions:
                for task_id, task in execution.tasks.items():
                    s = stats[task_id]
                    s["executions"] += 1
                    if task.status == TaskStatus.SUCCESS:
                        s["successes"] += 1
                    elif task.status == TaskStatus.FAILED:
                        s["failures"] += 1
                    if task.duration:
                        s["avg_duration"] = (s["avg_duration"] + task.duration) / 2

        return stats

    def get_report(self) -> str:
        """Generate execution report."""
        with self.lock:
            total = len(self.executions)
            successful = sum(1 for e in self.executions if e.status == WorkflowStatus.SUCCESS)
            failed = sum(1 for e in self.executions if e.status == WorkflowStatus.FAILED)

            report = f"""
Workflow Execution Report
========================
Total Executions: {total}
Successful: {successful}
Failed: {failed}
Success Rate: {self.get_success_rate():.1%}
Average Duration: {self.get_average_duration():.2f}s
"""
            return report

if __name__ == '__main__':
    # Setup basic logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 1. Create an EventLedger instance
    # Note: Adjust the path if you run this from a different directory
    import os
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'workflow_events.db')
    if os.path.exists(db_path):
        os.remove(db_path)

    ledger = EventLedger(db_path=db_path)
    logging.info(f"EventLedger initialized with db at {db_path}")

    # 2. Create a WorkflowExecutor instance with the ledger
    executor = WorkflowExecutor(max_workers=2, ledger=ledger)
    logging.info("WorkflowExecutor initialized with EventLedger.")

    # Define some simple task handlers
    def handler_a(context):
        print("Executing Task A")
        time.sleep(1)
        return {"result_a": "A completed"}

    def handler_b(context):
        print("Executing Task B, depends on A")
        print(f"Context from A: {context.get('task_a')}")
        time.sleep(1)
        return {"result_b": "B completed"}

    def handler_c(context):
        print("Executing Task C, depends on B")
        print(f"Context from B: {context.get('task_b')}")
        time.sleep(1)
        # This task will fail
        raise ValueError("Something went wrong in C")

    # 3. Define a workflow
    builder = WorkflowBuilder(workflow_id="wf-001", name="Test Workflow")
    builder.add_task(task_id="task_a", name="Task A", handler=handler_a, domain="processing")
    builder.add_task(task_id="task_b", name="Task B", handler=handler_b, domain="processing", depends_on=["task_a"])
    builder.add_task(task_id="task_c", name="Task C", handler=handler_c, domain="error_handling", depends_on=["task_b"], retries=1)

    workflow = builder.build()
    logging.info(f"Built workflow '{workflow.name}' with {len(workflow.tasks)} tasks.")

    # 4. Execute the workflow
    logging.info("Starting workflow execution...")
    execution_result = executor.execute(workflow)
    logging.info(f"Workflow execution finished with status: {execution_result.status}")

    # 5. Query the ledger to see the recorded events
    print("\n--- Recorded Events ---")
    all_events = ledger.query_events(limit=100)
    for event in reversed(all_events): # Print in chronological order
        print(f"[{event['timestamp']}] {event['event_type']} - Target: {event.get('target')} - Payload: {event.get('payload_json')}")
    
    ledger.close()
