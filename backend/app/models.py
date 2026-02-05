from sqlalchemy import Column, Integer, String, Text, ForeignKey
from .database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(String, nullable=False)
    task_ref = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, nullable=False, default="pending")
    assigned_to = Column(String, index=True)
    claimed_at = Column(String)
    completed_at = Column(String)
    outcome = Column(String)
    created_by = Column(String, nullable=False)
    priority = Column(Integer, default=0)
    tags = Column(Text)  # Stored as JSON string
    file_path = Column(String)
    file_synced_at = Column(String)

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(String, nullable=False)
    channel = Column(String, nullable=False, index=True)
    sender = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(String, nullable=False, default="text")
    reply_to = Column(String, ForeignKey("messages.id"))
    tags = Column(Text)  # Stored as JSON string
    metadata = Column(Text) # Stored as JSON string


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String, nullable=False)
    event_type = Column(String, nullable=False, index=True)
    actor = Column(String, nullable=False, index=True)
    target = Column(String)
    domain = Column(String, index=True)
    signal_type = Column(String)
    oracle_tier = Column(Integer)
    random_seed = Column(Integer)
    completion_promise = Column(String)
    verification_method = Column(String)
    payload_json = Column(Text)
    cost_tokens = Column(Integer)
    cost_usd = Column(Float)
    cost_carbon = Column(Float)


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending") # pending, approved, denied
    original_input = Column(Text, nullable=False)
    llm_hypothesis = Column(Text, nullable=False)
    proposed_hive_code = Column(Text, nullable=False)
    resolved_by = Column(String)
    resolved_at = Column(String)
