import os
from datetime import datetime
from ... import schemas # Assuming simdecisions is the top-level package

# Define the base path for file-driven communication
FILE_HIVE_BASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", ".deia", "hive"
)

def write_task_to_file(task: schemas.Task):
    """
    Writes a task to a Markdown file in the .deia/hive/tasks directory.
    """
    # Ensure the target directory exists
    tasks_path = os.path.join(FILE_HIVE_BASE_PATH, "tasks")
    os.makedirs(tasks_path, exist_ok=True)

    # Format filename: YYYY-MM-DD-HHMM-Q33N-{bee}-TASK-{id}.md
    # For now, we'll use a simplified format, as not all fields are available yet.
    timestamp_str = datetime.now().strftime("%Y-%m-%d-%H%M")
    filename = f"{timestamp_str}-TASK-{task.id}.md"
    file_path = os.path.join(tasks_path, filename)

    content = f"""# Task: {task.title}

**ID:** {task.id}
**Ref:** {task.task_ref}
**Status:** {task.status}
**Created By:** {task.created_by}
**Created At:** {task.created_at}

## Description
{task.description if task.description else "No description provided."}

---
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Task {task.id} written to file: {file_path}")
    return file_path
