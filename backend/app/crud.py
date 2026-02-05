from sqlalchemy.orm import Session
import uuid
import json
from datetime import datetime
from . import models, schemas

def get_task(db: Session, task_id: str):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(
        id=str(uuid.uuid4()),
        **task.model_dump()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task_file_sync_status(db: Session, task_id: str, file_path: str, synced_at: str):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db_task.file_path = file_path
        db_task.file_synced_at = synced_at
        db.commit()
        db.refresh(db_task)
    return db_task

def create_task_with_id(db: Session, task: schemas.TaskCreate, task_id: str):
    db_task = models.Task(
        id=task_id,
        **task.model_dump()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task_status(db: Session, task_id: str, status: str):
    db_task = get_task(db, task_id)
    if db_task:
        db_task.status = status
        db.commit()
        db.refresh(db_task)
    return db_task

def claim_task(db: Session, task_id: str, agent_id: str):
    db_task = get_task(db, task_id)
    if db_task and db_task.status == "pending":
        db_task.status = "in_progress"
        db_task.assigned_to = agent_id
        db_task.claimed_at = datetime.now().isoformat()
        db.commit()
        db.refresh(db_task)
    return db_task

def complete_task(db: Session, task_id: str, outcome: str = "success"):
    db_task = get_task(db, task_id)
    if db_task and db_task.status == "in_progress":
        db_task.status = "completed"
        db_task.outcome = outcome
        db_task.completed_at = datetime.now().isoformat()
        db.commit()
        db.refresh(db_task)
    return db_task

def log_event(db: Session, event_type: str, actor: str, payload: dict):
    """Logs a generic event to the event ledger."""
    db_event = models.Event(
        timestamp=datetime.now().isoformat(),
        event_type=event_type,
        actor=actor,
        payload_json=json.dumps(payload)
        # Other fields like domain, target, etc. can be populated as needed
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_events(db: Session, skip: int = 0, limit: int = 100):
    """Retrieves a list of events from the event ledger."""
    return db.query(models.Event).order_by(models.Event.timestamp.desc()).offset(skip).limit(limit).all()


# --- Approval CRUD Functions ---

def create_approval(db: Session, approval: schemas.ApprovalCreate):
    """Creates a new approval request."""
    db_approval = models.Approval(
        id=str(uuid.uuid4()),
        created_at=datetime.now().isoformat(),
        **approval.model_dump()
    )
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)
    return db_approval

def get_approval(db: Session, approval_id: str):
    """Retrieves a single approval request by its ID."""
    return db.query(models.Approval).filter(models.Approval.id == approval_id).first()

def get_pending_approvals(db: Session, skip: int = 0, limit: int = 100):
    """Retrieves a list of all pending approval requests."""
    return db.query(models.Approval).filter(models.Approval.status == "pending").order_by(models.Approval.created_at).offset(skip).limit(limit).all()

def resolve_approval(db: Session, approval_id: str, update: schemas.ApprovalUpdate):
    """Resolves an approval request by setting its status (approved/denied)."""
    db_approval = get_approval(db, approval_id)
    if db_approval and db_approval.status == "pending":
        db_approval.status = update.status
        db_approval.resolved_by = update.resolved_by
        db_approval.resolved_at = datetime.now().isoformat()
        db.commit()
        db.refresh(db_approval)
    return db_approval
