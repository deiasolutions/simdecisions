import requests
import time
import os
import re

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
AGENT_ID = "BEE-001"

def find_pending_task():
    """Finds the first 'pending' task from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/tasks/")
        response.raise_for_status()
        tasks = response.json()
        for task in tasks:
            if task.get("status") == "pending":
                print(f"Found pending task: {task['id']} - {task['title']}")
                return task
        return None
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to API: {e}")
        return None

def claim_task_by_file(task: dict):
    """Claims a task by modifying its Markdown file."""
    file_path = task.get("file_path")
    if not file_path or not os.path.exists(file_path):
        print(f"Error: Task file path not found or does not exist: {file_path}")
        return False
    
    print(f"Claiming task {task['id']} by modifying file...")
    
    # Read content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Modify status and add assignee
    content = re.sub(r"(\*\*Status:\*\*\s*)pending", r"\g<1>in_progress", content)
    
    # Check if assignee line exists
    if "Assigned To" in content:
         content = re.sub(r"(\*\*Assigned To:\*\*\s*).*", rf"\g<1>{AGENT_ID}", content)
    else:
        # Add assignee line
        content = content.replace("## Description", f"**Assigned To:** {AGENT_ID}

## Description")

    # Write content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Task claimed.")
    return True

def complete_task_by_file(task: dict):
    """Completes a task by modifying its Markdown file."""
    file_path = task.get("file_path")
    if not file_path or not os.path.exists(file_path):
        print(f"Error: Task file path not found or does not exist: {file_path}")
        return False

    print(f"Completing task {task['id']} by modifying file...")
    
    # Read content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Modify status
    content = re.sub(r"(\*\*Status:\*\*\s*)in_progress", r"\g<1>completed", content)
    
    # Write content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Task completed.")
    return True


def main():
    """Main loop for the Hello Bee agent."""
    print(f"Hello Bee ({AGENT_ID}) starting work cycle...")
    
    # 1. Find a task
    task = find_pending_task()
    if not task:
        print("No pending tasks found. Bee is going to sleep.")
        return

    # 2. Claim the task by modifying its file
    if not claim_task_by_file(task):
        return

    # 3. "Work" on the task
    print("Working on the task...")
    time.sleep(3) # Simulate work

    # 4. Complete the task by modifying its file
    complete_task_by_file(task)
    
    print("Work cycle complete.")


if __name__ == "__main__":
    # Ensure backend requirements.txt includes 'requests' if this is run in the same venv
    main()
