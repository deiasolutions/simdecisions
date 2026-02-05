from pydantic import BaseModel
from typing import List, Optional, Any
import datetime

# Base schema for a Task
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    task_ref: str
    created_by: str
    priority: Optional[int] = 0

# Schema for creating a task
class TaskCreate(TaskBase):
    pass

# Schema for reading a task (includes fields from the DB)
class Task(TaskBase):
    id: str
    created_at: Any # Using Any to avoid issues with str from db
    status: str
    assigned_to: Optional[str] = None
    file_path: Optional[str] = None
    file_synced_at: Optional[Any] = None # Using Any to avoid issues with str from db
    
    class Config:
        from_attributes = True

# Base schema for a Message
class MessageBase(BaseModel):
    channel: str
    sender: str
    content: str
    message_type: Optional[str] = 'text'

# Schema for creating a message
class MessageCreate(MessageBase):
    pass

# Schema for reading a message
class Message(MessageBase):
    id: str

    created_at: Any  # Using Any to avoid issues with str from db
    
    class Config:
        from_attributes = True

class HiveCodeRequest(BaseModel):
    code: str


class TaskStatusUpdate(BaseModel):
    status: str

class TaskClaim(BaseModel):
    agent_id: str

class TaskCompletion(BaseModel):
    outcome: str = "success"


class Event(BaseModel):
    id: int
    timestamp: Any
    event_type: str
    actor: str
    target: Optional[str] = None
    domain: Optional[str] = None
    payload_json: Optional[str] = None

    class Config:
        from_attributes = True
