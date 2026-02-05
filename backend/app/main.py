from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import threading
from contextlib import asynccontextmanager

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db
from .synchronizer import file_synchronizer
from .synchronizer.file_watcher import start_file_watcher, TASKS_PATH

# This command creates the database tables if they don't exist.
# In a production app, you would use a migration tool like Alembic.
models.Base.metadata.create_all(bind=engine)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting file watcher thread...")
    global observer_thread
    observer_thread = threading.Thread(target=start_file_watcher, daemon=True)
    observer_thread.start()
    print(f"File watcher thread started, monitoring: {TASKS_PATH}")
    yield
    # Shutdown
    print("Stopping file watcher thread...")
    # For now, the daemon thread exits with the main process.
    # Proper shutdown would require the observer object to be returned and stopped.

app = FastAPI(title="SimDecisions Hive Control Plane", lifespan=lifespan)

@app.post("/api/v1/tasks/", response_model=schemas.Task)
def create_task_endpoint(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = crud.create_task(db=db, task=task)
    
    # One-way sync: write task to file system
    file_path_full = file_synchronizer.write_task_to_file(db_task)
    
    # Update the database record with file sync status
    synced_at_str = datetime.now().isoformat()
    crud.update_task_file_sync_status(db, db_task.id, file_path_full, synced_at_str)
    
    return db_task

@app.get("/api/v1/tasks/", response_model=List[schemas.Task])
def read_tasks_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks

@app.get("/api/v1/events/", response_model=List[schemas.Event], summary="Read the Event Ledger")
def read_events_endpoint(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Retrieves the most recent events from the Event Ledger.
    """
    events = crud.get_events(db, skip=skip, limit=limit)
    return events

@app.get("/api/v1/tasks/{task_id}", response_model=schemas.Task)
def read_task_endpoint(task_id: str, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/api/v1/tasks/{task_id}/status", response_model=schemas.Task)
def update_task_status_endpoint(task_id: str, status_update: schemas.TaskStatusUpdate, db: Session = Depends(get_db)):
    db_task = crud.update_task_status(db, task_id=task_id, status=status_update.status)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.post("/api/v1/tasks/{task_id}/claim", response_model=schemas.Task)
def claim_task_endpoint(task_id: str, claim_request: schemas.TaskClaim, db: Session = Depends(get_db)):
    db_task = crud.claim_task(db, task_id=task_id, agent_id=claim_request.agent_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found or not in 'pending' state")
    return db_task

@app.post("/api/v1/tasks/{task_id}/complete", response_model=schemas.Task)
def complete_task_endpoint(task_id: str, completion_request: schemas.TaskCompletion, db: Session = Depends(get_db)):
    db_task = crud.complete_task(db, task_id=task_id, outcome=completion_request.outcome)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found or not 'in_progress'")
    return db_task


# --- Approval Endpoints ---

@app.get("/api/v1/approvals/pending", response_model=List[schemas.Approval], summary="List Pending Approvals")
def get_pending_approvals_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of all approval requests with a 'pending' status.
    """
    return crud.get_pending_approvals(db, skip=skip, limit=limit)

@app.post("/api/v1/approvals/{approval_id}/resolve", response_model=schemas.Approval, summary="Resolve an Approval")
def resolve_approval_endpoint(approval_id: str, update: schemas.ApprovalUpdate, db: Session = Depends(get_db)):
    """
    Approves or denies a pending approval request.
    If approved, the proposed Hive Code is then executed.
    """
    db_approval = crud.get_approval(db, approval_id)
    if db_approval is None or db_approval.status != 'pending':
        raise HTTPException(status_code=404, detail="Pending approval not found")

    resolved_approval = crud.resolve_approval(db, approval_id=approval_id, update=update)

    if resolved_approval and resolved_approval.status == 'approved':
        print(f"Executing approved Hive Code for approval {approval_id}")
        # Execute the approved code
        try:
            # We re-use the Hive Code executor logic
            # This could be refactored into a shared service
            tree = hive_parser.parse(resolved_approval.proposed_hive_code)
            executor = HiveCodeExecutor(db=db)
            executor.transform(tree)
            # TODO: Log the successful execution event
        except Exception as e:
            # TODO: Log the failed execution event
            print(f"Error executing approved Hive Code: {e}")
            # The approval is already marked 'approved', we might need a new status like 'execution_failed'
            pass

    return resolved_approval

from language import translator
from language.translator import ClarificationNeededError

# ... (keep existing imports, app setup, lifespan, and task/approval endpoints)


# --- COMMAND ENDPOINT (SCRIPT & HIVE CODE) ---

# Hive Code Parser (still needed for executing translated or approved code)
hive_grammar = r"""
    ?start: command
    command: create_task | list_tasks | get_task | assign_task
    create_task: "SORTU" "ZEREGINA" ESCAPED_STRING "izenburuarekin" ("eta" ESCAPED_STRING "deskribapenarekin")? -> create_task
    list_tasks: "ZERRENDATU" "ZEREGINAK" (ESCAPED_STRING "egoerarekin")? -> list_tasks
    get_task: "LORTU" "ZEREGINA" ESCAPED_STRING -> get_task
    assign_task: "ESLEITU" "ZEREGINA" ESCAPED_STRING ESCAPED_STRING "eragileari" -> assign_task
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
"""
hive_parser = Lark(hive_grammar, start='command', parser='lalr', case_sensitive=True)

class HiveCodeExecutor(Transformer):
    # ... (HiveCodeExecutor class from previous step remains the same)
    def __init__(self, db: Session):
        self.db = db

    def ESCAPED_STRING(self, s):
        return s[1:-1]

    def create_task(self, items):
        title = items[2]
        description = items[4] if len(items) > 4 else None
        
        task_create = schemas.TaskCreate(
            title=title, description=description, task_ref="HIVE-CODE-TASK", created_by="HiveCode"
        )
        db_task = crud.create_task(db=self.db, task=task_create)
        file_path = file_synchronizer.write_task_to_file(db_task)
        synced_at = datetime.now().isoformat()
        crud.update_task_file_sync_status(self.db, db_task.id, file_path, synced_at)
        return db_task

    def list_tasks(self, items):
        return crud.get_tasks(db=self.db)
        
    def get_task(self, items):
        task_id = items[2]
        task = crud.get_task(db=self.db, task_id=task_id)
        if task is None: raise HTTPException(status_code=404, detail="Task not found")
        return task

    def assign_task(self, items):
        task_id, agent_id = items[2], items[3]
        task = crud.get_task(db=self.db, task_id=task_id)
        if task is None: raise HTTPException(status_code=404, detail="Task not found")
        task.assigned_to = agent_id
        self.db.add(task)
        self.db.commit()
        return task

def execute_hive_code_string(hive_code: str, db: Session):
    """Parses and executes a given Hive Code string."""
    event_payload = {"input_hive_code": hive_code, "execution_success": False, "error": None}
    try:
        tree = hive_parser.parse(hive_code)
        executor = HiveCodeExecutor(db=db)
        result = executor.transform(tree)
        event_payload["execution_success"] = True
        crud.log_event(db=db, event_type="hive_code_executed", actor="HiveCodeExecutor", payload=event_payload)
        return result
    except Exception as e:
        event_payload["error"] = str(e)
        crud.log_event(db=db, event_type="hive_code_executed", actor="HiveCodeExecutor", payload=event_payload)
        raise HTTPException(status_code=400, detail=f"Invalid or unsupported Hive Code: {e}")

@app.post("/api/v1/script-command/", summary="Execute a Script Language command")
def execute_script_command(request: schemas.ScriptCommandRequest, db: Session = Depends(get_db)):
    """
    Translates Script Language to Hive Code and executes it.
    If translation is ambiguous, it creates an Approval request for human review.
    """
    try:
        # Attempt to translate Script Language to Hive Code
        hive_code = translator.translate_script_to_hive_code(request.code)
        # If successful, execute it
        return execute_hive_code_string(hive_code, db)

    except ClarificationNeededError as e:
        # If the translator needs clarification, create an approval request
        approval_create = schemas.ApprovalCreate(
            original_input=request.code,
            llm_hypothesis=e.message,
            proposed_hive_code=e.proposed_hive_code or ""
        )
        approval = crud.create_approval(db=db, approval=approval_create)
        raise HTTPException(
            status_code=202, # Accepted for later processing
            detail={
                "message": "Command is ambiguous and requires human approval.",
                "approval_request_id": approval.id,
                "clarification_needed": e.message
            }
        )
    except ValueError as e:
        # Handle general translation value errors
        raise HTTPException(status_code=400, detail=f"Could not translate script: {e}")


@app.get("/")
def read_root():
    return {"message": "SimDecisions Hive Control Plane is running."}
