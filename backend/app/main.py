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

from lark import Lark, Transformer

# ... (keep existing imports)

# ... (keep existing app setup and lifespan)

# ... (keep existing task endpoints)


# --- HIVE CODE EXECUTOR ---

# Grammar for the Basque-based Hive Code
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

class HiveCodeExecutor(Transformer):
    def __init__(self, db: Session):
        self.db = db

    def ESCAPED_STRING(self, s):
        return s[1:-1]

    def create_task(self, items):
        title = items[2]
        description = items[4] if len(items) > 4 else None
        
        task_create = schemas.TaskCreate(
            title=title,
            description=description,
            task_ref="HIVE-CODE-TASK", # Default ref
            created_by="HiveCode" # Default creator
        )
        db_task = crud.create_task(db=self.db, task=task_create)

        # Trigger one-way file sync
        file_path = file_synchronizer.write_task_to_file(db_task)
        synced_at = datetime.now().isoformat()
        crud.update_task_file_sync_status(self.db, db_task.id, file_path, synced_at)
        
        return db_task

    def list_tasks(self, items):
        status = items[2] if len(items) > 2 else None
        # TODO: Implement filtering in crud.get_tasks
        if status:
            print(f"Filtering by status: {status}") # Placeholder
        return crud.get_tasks(db=self.db)
        
    def get_task(self, items):
        task_id = items[2]
        task = crud.get_task(db=self.db, task_id=task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def assign_task(self, items):
        task_id, agent_id = items[2], items[3]
        # TODO: Implement crud.assign_task function
        print(f"Assigning task {task_id} to agent {agent_id}") # Placeholder
        task = crud.get_task(db=self.db, task_id=task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        task.assigned_to = agent_id
        self.db.add(task)
        self.db.commit()
        return task

# Initialize Hive Code parser
hive_parser = Lark(hive_grammar, start='command', parser='lalr', case_sensitive=True)

@app.post("/api/v1/hive-code/", summary="Execute a Hive Code command")
def execute_hive_code(request: schemas.HiveCodeRequest, db: Session = Depends(get_db)):
    """
    Parses and executes a Basque-based Hive Code string, and logs the event.
    """
    event_payload = {
        "input_hive_code": request.code,
        "execution_success": False,
        "error": None
    }
    try:
        tree = hive_parser.parse(request.code)
        executor = HiveCodeExecutor(db=db)
        result = executor.transform(tree)
        
        # If we reach here, execution was successful
        event_payload["execution_success"] = True
        
        # Log the successful event
        crud.log_event(
            db=db,
            event_type="hive_code_executed",
            actor="HiveCodeEndpoint", # Or get user from auth
            payload=event_payload
        )
        
        return result
    except Exception as e:
        # Log the failed event
        event_payload["error"] = str(e)
        crud.log_event(
            db=db,
            event_type="hive_code_executed",
            actor="HiveCodeEndpoint",
            payload=event_payload
        )
        raise HTTPException(status_code=400, detail=f"Invalid or unsupported Hive Code: {e}")

@app.get("/")
def read_root():
    return {"message": "SimDecisions Hive Control Plane is running."}
