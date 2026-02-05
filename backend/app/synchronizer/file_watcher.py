import os
import time
import re
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

from ..database import SessionLocal
from .. import crud, schemas
from sqlalchemy.orm import Session
from .llm_resolver import LLMConflictResolver, Resolution

# Define the base path for file-driven communication
FILE_HIVE_BASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", ".deia", "hive"
)
TASKS_PATH = os.path.join(FILE_HIVE_BASE_PATH, "tasks")

def parse_task_file(file_path: str) -> dict:
    """
    Parses a Markdown task file and extracts task data.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        title_match = re.search(r"# Task: (.+)", content)
        id_match = re.search(r"\*\*ID:\*\*\s*(.+)", content)
        ref_match = re.search(r"\*\*Ref:\*\*\s*(.+)", content)
        status_match = re.search(r"\*\*Status:\*\*\s*(.+)", content)
        description_match = re.search(r"## Description\s*([\s\S]+?)---", content)
        description = description_match.group(1).strip() if description_match else ""

        task_id = id_match.group(1).strip() if id_match else None
        if not task_id:
            print(f"WARNING: Could not find ID in file {file_path}. Skipping.")
            return None

        return {
            "id": task_id,
            "title": title_match.group(1).strip() if title_match else "Untitled Task",
            "description": description,
            "task_ref": ref_match.group(1).strip() if ref_match else f"REF-{task_id[:8]}",
            "status": status_match.group(1).strip() if status_match else "pending",
        }
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return None

class TaskFileEventHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.resolver = LLMConflictResolver()

    def _process_file(self, file_path: str, event_type: str):
        if not file_path.endswith(".md"):
            return

        print(f"Processing {event_type} event for file: {file_path}")

        file_data = parse_task_file(file_path)
        if file_data is None:
            return

        db: Session = None
        try:
            db = SessionLocal()
            existing_task = crud.get_task(db, file_data["id"])

            if not existing_task:
                print(f"Task {file_data['id']} not found in DB. Logic for file-only creation to be added.")
                # TODO: Add logic for creating a new task from a file if that's desired
                return

            # Conflict Detected: A file has been modified for a task that exists in the database.
            print(f"Conflict detected for task {existing_task.id}. Invoking LLM resolver.")

            version_a = schemas.Task.from_orm(existing_task).model_dump()
            version_b = file_data
            context = {"schema": schemas.Task.schema(), "process_rules": ["PROCESS-0002"]}

            # Run the async resolve method
            resolution = asyncio.run(self.resolver.resolve(version_a, version_b, context))
            print(f"Resolution from LLM ({resolution.model_used}): {resolution.resolution} - {resolution.reason}")

            if resolution.resolution == "escalate":
                print(f"ESCALATION REQUIRED for task {existing_task.id}: {resolution.reason}")
                # TODO: Implement escalation logic (e.g., notify human via dashboard)
            elif resolution.resolution == "pick_a":
                # Version A (DB) wins. No change needed, but log it.
                print("Resolution is to keep the database version. No changes made.")
            elif resolution.resolution == "pick_b":
                # Version B (File) wins. Update DB with file content.
                existing_task.title = file_data["title"]
                existing_task.description = file_data["description"]
                existing_task.status = file_data["status"]
                db.add(existing_task)
                db.commit()
                print("Database updated with content from file.")
            elif resolution.resolution == "merge" and resolution.merged_data:
                # Merge wins. Update DB with merged content.
                merged_data = resolution.merged_data
                existing_task.title = merged_data.get("title", existing_task.title)
                existing_task.description = merged_data.get("description", existing_task.description)
                existing_task.status = merged_data.get("status", existing_task.status)
                db.add(existing_task)
                db.commit()
                print("Database updated with merged content from LLM.")

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            if db: db.rollback()
        finally:
            if db: db.close()

    def on_modified(self, event):
        if not event.is_directory:
            self._process_file(event.src_path, "modified")

    # on_created can also call _process_file, but for now we focus on modifications as the conflict point
    def on_created(self, event):
        if not event.is_directory:
             print(f"File created: {event.src_path}. Processing as potential new task.")
             self._process_file(event.src_path, "created")


def start_file_watcher():
    """Starts an observer to watch for changes in the .deia/hive/tasks directory."""
    event_handler = TaskFileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, TASKS_PATH, recursive=False)
    observer.start()
    print(f"File watcher started, monitoring: {TASKS_PATH}")
    return observer

if __name__ == "__main__":
    observer = start_file_watcher()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
