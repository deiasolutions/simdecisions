import click
import requests
import json

API_BASE_URL = "http://127.0.0.1:8000/api/v1" # Local development URL

@click.group()
def sd():
    """SimDecisions CLI"""
    pass

@sd.group()
def task():
    """Manage tasks."""
    pass

@task.command("create")
@click.option("--title", required=True, help="Title of the task.")
@click.option("--description", default=None, help="Description of the task.")
@click.option("--ref", help="Reference ID for the task.", default="CLI-TASK")
@click.option("--created-by", help="Creator of the task.", default="sd-cli")
def create_task(title, description, ref, created_by):
    """Create a new task."""
    payload = {
        "title": title,
        "description": description,
        "task_ref": ref,
        "created_by": created_by,
    }
    try:
        response = requests.post(f"{API_BASE_URL}/tasks/", json=payload)
        response.raise_for_status()
        click.echo(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        click.echo(f"Error creating task: {e}")
        click.echo(f"Response: {e.response.text}" if e.response else "")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")

@task.command("list")
@click.option("--status", default=None, help="Filter tasks by status (e.g., pending, in_progress, completed).")
@click.option("--limit", type=int, default=10, help="Limit the number of tasks returned.")
@click.option("--skip", type=int, default=0, help="Skip the first N tasks.")
def list_tasks(status, limit, skip):
    """List tasks."""
    params = {"skip": skip, "limit": limit}
    if status:
        params["status"] = status
    try:
        response = requests.get(f"{API_BASE_URL}/tasks/", params=params)
        response.raise_for_status()
        tasks = response.json()
        if not tasks:
            click.echo("No tasks found.")
            return
        for t in tasks:
            click.echo(f"ID: {t['id']}")
            click.echo(f"  Title: {t['title']}")
            click.echo(f"  Status: {t['status']}")
            click.echo(f"  Created By: {t['created_by']}")
            click.echo(f"  Assigned To: {t['assigned_to']}")
            click.echo("-" * 20)
    except requests.exceptions.RequestException as e:
        click.echo(f"Error listing tasks: {e}")
        click.echo(f"Response: {e.response.text}" if e.response else "")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")

@task.command("show")
@click.argument("task_id")
def show_task(task_id):
    """Show details of a specific task."""
    try:
        response = requests.get(f"{API_BASE_URL}/tasks/{task_id}")
        response.raise_for_status()
        click.echo(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        click.echo(f"Error showing task {task_id}: {e}")
        if e.response and e.response.status_code == 404:
            click.echo(f"Task with ID {task_id} not found.")
        else:
            click.echo(f"Response: {e.response.text}" if e.response else "")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")

@task.command("update")
@click.argument("task_id")
@click.option("--status", required=True, help="New status for the task.")
def update_task(task_id, status):
    """Update the status of a task."""
    try:
        response = requests.put(f"{API_BASE_URL}/tasks/{task_id}/status", json={"status": status})
        response.raise_for_status()
        click.echo(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        click.echo(f"Error updating task {task_id}: {e}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")

@task.command("claim")
@click.argument("task_id")
@click.option("--agent-id", default="sd-cli-agent", help="ID of the agent claiming the task.")
def claim_task(task_id, agent_id):
    """Claim a pending task."""
    try:
        response = requests.post(f"{API_BASE_URL}/tasks/{task_id}/claim", json={"agent_id": agent_id})
        response.raise_for_status()
        click.echo(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        click.echo(f"Error claiming task {task_id}: {e}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")

@task.command("complete")
@click.argument("task_id")
@click.option("--outcome", default="success", help="Outcome of the task (e.g., success, failure).")
def complete_task(task_id, outcome):
    """Mark a task as complete."""
    try:
        response = requests.post(f"{API_BASE_URL}/tasks/{task_id}/complete", json={"outcome": outcome})
        response.raise_for_status()
        click.echo(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        click.echo(f"Error completing task {task_id}: {e}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    sd()
