---
name: task
description: Quick task creation and assignment. Create tasks and optionally assign to agents and set status in one command.
---

# Task Creation Skill

**Trigger**: `/task "title" [agent] [status]`
**Purpose**: Quickly create and assign tasks

## Usage Examples

```bash
# Create task in inbox
/task "Implement Swagger documentation"

# Create and assign to engineer (auto-sets to ready-to-build)
/task "Add user authentication" engineer

# Create, assign, and set specific status
/task "Fix login bug" engineer in-progress

# Create for QA
/task "Test payment flow" qa ready-for-testing
```

## Implementation

```python
import sys
import os
from datetime import datetime
from pathlib import Path
import re

# Plugin initialization
def get_plugin_dir():
    if '__file__' in globals():
        return Path(__file__).resolve().parent.parent.parent
    return Path.home() / '.claude/plugins/cache/agentic-workflow'

PLUGIN_DIR = get_plugin_dir()
sys.path.insert(0, str(PLUGIN_DIR / 'lib'))

from task_manager import get_task_manager
from activity import log_activity

# Parse arguments
if len(args) == 0:
    print("❌ Task title required")
    print("")
    print("Usage:")
    print("  /task \"Task title\"")
    print("  /task \"Task title\" agent")
    print("  /task \"Task title\" agent status")
    print("")
    print("Examples:")
    print("  /task \"Implement Swagger docs\"")
    print("  /task \"Add auth endpoint\" engineer")
    print("  /task \"Fix bug\" engineer in-progress")
    print("")
    print("Available agents: pm, architect, engineer, qa, devops")
    print("Available statuses: inbox, in-planning, ready-to-build, in-progress,")
    print("                    ready-for-testing, in-qa, ready-to-deploy")
    sys.exit(1)

title = args[0]
agent = args[1] if len(args) > 1 else None
status = args[2] if len(args) > 2 else None

# Auto-determine status based on agent if not specified
if agent and not status:
    status_map = {
        'pm': 'inbox',
        'architect': 'in-planning',
        'engineer': 'ready-to-build',
        'qa': 'ready-for-testing',
        'devops': 'ready-to-deploy'
    }
    status = status_map.get(agent, 'inbox')

# Default to inbox if no agent specified
if not status:
    status = 'inbox'

print(f"📝 Creating task: {title}")
print("")

# Ensure workspace exists
workspace = Path.cwd() / 'workspace'
if not workspace.exists():
    print("⚠️  No workspace found. Creating one...")
    from pathlib import Path
    import shutil

    template = PLUGIN_DIR / 'lib/templates/workspace'
    if template.exists():
        shutil.copytree(template, workspace)
        print("✅ Workspace created")
    else:
        # Create minimal workspace
        dirs = [
            'agents/pm', 'agents/architect', 'agents/engineer',
            'agents/qa', 'agents/devops',
            'tasks/inbox', 'tasks/in-discovery', 'tasks/in-planning',
            'tasks/ready-to-build', 'tasks/in-progress',
            'tasks/ready-for-testing', 'tasks/in-qa',
            'tasks/ready-to-deploy', 'tasks/deployed',
            'docs/specs', 'docs/plans'
        ]
        for d in dirs:
            (workspace / d).mkdir(parents=True, exist_ok=True)
        (workspace / 'activity.log').touch()
        print("✅ Minimal workspace created")
    print("")

# Generate task ID
tm = get_task_manager('workspace')

# Find next task ID
existing_tasks = list(Path('workspace/tasks').rglob('task-*.md'))
if existing_tasks:
    # Extract numbers from task filenames
    task_nums = []
    for task_file in existing_tasks:
        match = re.search(r'task-(\d+)', task_file.name)
        if match:
            task_nums.append(int(match.group(1)))
    next_num = max(task_nums) + 1 if task_nums else 1
else:
    next_num = 1

task_id = f"task-{next_num:03d}"

# Create task
print(f"🆔 Task ID: {task_id}")
print(f"📂 Status: {status}")
if agent:
    print(f"👤 Assigned: {agent}")
print("")

# Create task content
task_content = f"""---
id: {task_id}
title: {title}
status: {status}
priority: P2
created: {datetime.now().isoformat()}
updated: {datetime.now().isoformat()}
assigned: [{f'"{agent}"' if agent else ''}]
---

# {title}

## Description

{title}

## Acceptance Criteria

- [ ] Feature works as described
- [ ] Tests are written
- [ ] Code is reviewed

## Thread

- **human** ({datetime.now().strftime('%Y-%m-%d %H:%M')}): Task created via /task command
"""

if agent:
    task_content += f"- **{agent}** ({datetime.now().strftime('%Y-%m-%d %H:%M')}): Assigned to {agent}\n"

# Write task file
task_file = workspace / f'tasks/{status}/{task_id}.md'
task_file.parent.mkdir(parents=True, exist_ok=True)
task_file.write_text(task_content)

# Log activity
log_activity('task-creator', f'Created {task_id}: {title}')
if agent:
    log_activity('task-creator', f'Assigned {task_id} to {agent} in {status}')

print("✅ Task created successfully!")
print("")
print(f"📄 File: workspace/tasks/{status}/{task_id}.md")
print("")

# Show next steps
if agent:
    print("Run agent:")
    print(f"  /{agent} {task_id}")
else:
    print("Start workflow:")
    print(f"  /work {task_id}")
    print("")
    print("Or assign to specific agent:")
    print(f"  /task \"{title}\" engineer")

print("")
print("View task:")
print(f"  cat workspace/tasks/{status}/{task_id}.md")
```

## Status Mapping

When you provide an agent but no status, the skill automatically selects the appropriate status:

| Agent | Auto Status |
|-------|-------------|
| pm | inbox |
| architect | in-planning |
| engineer | ready-to-build |
| qa | ready-for-testing |
| devops | ready-to-deploy |

## Advanced Examples

```bash
# Create a bug fix task
/task "Fix null pointer exception in auth" engineer in-progress

# Create a testing task
/task "Verify payment integration" qa ready-for-testing

# Create a deployment task
/task "Deploy v2.1.0 to staging" devops ready-to-deploy

# Create a planning task
/task "Design microservices architecture" architect in-planning

# Create multiple tasks quickly
/task "Add user profile endpoint" engineer
/task "Add company profile endpoint" engineer
/task "Add admin dashboard endpoint" engineer
```

## Tips

- **Quick workflow**: Use `/task "title" engineer` to skip PM/Architect and go straight to implementation
- **Testing**: Use `/task "title" qa` to create tasks for QA testing
- **Task ID**: Automatically increments (task-001, task-002, etc.)
- **Workspace**: Auto-creates if doesn't exist
- **Activity log**: All task creation is logged
