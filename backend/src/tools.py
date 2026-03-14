import json
import os
from langchain_core.tools import tool

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROJECTS_FILE = os.path.join(DATA_DIR, 'projects.json')
TODOS_FILE = os.path.join(DATA_DIR, 'todos.txt')
BIO_FILE = os.path.join(DATA_DIR, 'bio.md')

@tool
def get_projects(query: str = "") -> str:
    """
    Search for projects in the user's portfolio. 
    If query is empty, lists all projects.
    Returns JSON string of matching projects.
    """
    if not os.path.exists(PROJECTS_FILE):
        return "No projects file found."
    
    try:
        with open(PROJECTS_FILE, 'r') as f:
            projects = json.load(f)
        
        if not query:
            return json.dumps(projects, indent=2)
        
        # Simple search
        results = [
            p for p in projects 
            if query.lower() in p['name'].lower() or query.lower() in p['description'].lower()
        ]
        return json.dumps(results, indent=2) if results else "No matching projects found."
    except Exception as e:
        return f"Error reading projects: {str(e)}"

@tool
def manage_todos(command: str) -> str:
    """
    Manage a simple todo list.
    Input format: "action: task"
    Actions: 
    - "list": List all tasks (e.g., "list")
    - "add": Add a task (e.g., "add: Buy coffee")
    - "remove": Remove a task by index or name (e.g., "remove: 1" or "remove: coffee")
    - "clear": Clear all tasks (e.g., "clear")
    """
    if ":" in command:
        parts = command.split(":", 1)
        action = parts[0].strip().lower()
        task = parts[1].strip()
    else:
        action = command.strip().lower()
        task = ""

    if not os.path.exists(TODOS_FILE):
        with open(TODOS_FILE, 'w') as f:
            f.write("")

    try:
        with open(TODOS_FILE, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if action == "list":
            if not lines:
                return "Todo list is empty."
            return "\n".join([f"{i+1}. {line}" for i, line in enumerate(lines)])
        
        elif action == "add":
            if not task:
                return "Task description required to add."
            lines.append(f"[ ] {task}")
            with open(TODOS_FILE, 'w') as f:
                f.write("\n".join(lines))
            return f"Added task: {task}"
            
        elif action == "remove":
            # task can be index or string matching
            if task.isdigit():
                idx = int(task) - 1
                if 0 <= idx < len(lines):
                    removed = lines.pop(idx)
                    with open(TODOS_FILE, 'w') as f:
                        f.write("\n".join(lines))
                    return f"Removed task: {removed}"
                return "Invalid task index."
            else:
                # String match removal
                original_len = len(lines)
                lines = [l for l in lines if task.lower() not in l.lower()]
                if len(lines) < original_len:
                    with open(TODOS_FILE, 'w') as f:
                        f.write("\n".join(lines))
                    return f"Removed tasks matching '{task}'"
                return "No matching task found."
                
        elif action == "clear":
            with open(TODOS_FILE, 'w') as f:
                f.write("")
            return "Cleared all tasks."
            
        return "Invalid action. Use list, add: task, remove: task/index, or clear."

    except Exception as e:
        return f"Error managing todos: {str(e)}"

@tool
def get_personal_bio(query: str = "") -> str:
    """
    Read the user's personal manifesto and bio.
    Use this to understand the user's values, communication style, and non-technical interests.
    """
    if not os.path.exists(BIO_FILE):
        return "Bio file not found."
    try:
        with open(BIO_FILE, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading bio: {e}"
