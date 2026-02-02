# Agent Quick Start — File System Operations

**For all agents: How to work with the file-system workspace**

---

## On Every Invocation

### 1. Read Your Memory (ALWAYS DO THIS FIRST)

```python
# Read SOUL.md (who am I?)
soul = read_file("workspace/agents/{your_role}/SOUL.md")

# Read WORKING.md (what am I doing right now?)
working = read_file("workspace/agents/{your_role}/WORKING.md")

# Read today's log (what happened today?)
import datetime
today = datetime.datetime.now().strftime('%Y-%m-%d')
daily_log = read_file(f"workspace/agents/{your_role}/{today}.md")
```

### 2. Check for Work

```python
import sys
sys.path.append('agents/src')

from task_manager import get_task_manager
from notifications import check_notifications

# Check notifications first
notifs = check_notifications('{your_role}')
if notifs:
    print(f"📬 You have {len(notifs)} notifications")
    for n in notifs:
        print(f"  From {n['from']}: {n['message']}")

# Find work
tm = get_task_manager('workspace')
task = tm.find_work('{your_role}')

if task:
    print(f"📋 Found work: {task.title} ({task.id})")
```

---

## Common Operations

### Create Task (PM Agent)

```python
from task_manager import create_task

task = create_task(
    title="Build user authentication",
    description="Implement JWT auth with 2FA",
    priority="P1",
    tags=["backend", "security"]
)

# Task created in workspace/tasks/inbox/
```

### Assign Task to Yourself

```python
tm = get_task_manager('workspace')
tm.assign_task(task.id, '{your_role}')
```

### Move Task to New Status

```python
# When you start working
tm.move_task(task.id, 'in-progress')

# When done
tm.move_task(task.id, 'ready-for-testing')
```

### Add Comment

```python
tm.add_comment(
    task.id,
    '{your_role}',
    "Started implementation. Created API endpoints."
)
```

### Add Comment with @mention

```python
tm.add_comment(
    task.id,
    '{your_role}',
    "@security Can you review the JWT implementation?"
)
# Security agent will get notified automatically
```

### Update Task Fields

```python
tm.update_task(
    task.id,
    prd="docs/specs/authentication.md",
    plan="docs/plans/authentication.md",
    pr="https://github.com/user/repo/pull/123"
)
```

### Log Activity

```python
from activity import log_activity

log_activity('{your_role}', "Completed auth API implementation")
```

### Update Your WORKING.md

```python
working_content = f"""# WORKING — Current State

**Last Updated:** {datetime.datetime.now().isoformat()[:16]}

---

## Current Task

**Task ID:** {task.id}
**Title:** {task.title}
**Status:** In progress - writing tests

**What I'm doing:**
Implementing JWT authentication API

---

## Progress

**Completed:**
- [x] Created API endpoints
- [x] Added input validation

**In Progress:**
- [ ] Writing unit tests

**Next Steps:**
1. Finish unit tests
2. Run security scan
3. Create PR

---

## Quick Resume

Implementing JWT auth. Endpoints done, currently writing tests.
Need to run security scan before creating PR.
"""

write_file("workspace/agents/{your_role}/WORKING.md", working_content)
```

### Append to Daily Log

```python
log_entry = f"""
## {datetime.datetime.now().strftime('%H:%M')} - {activity_description}

{details}
"""

# Read existing
daily_log = read_file(f"workspace/agents/{your_role}/{today}.md")

# Append
daily_log += log_entry

# Write back
write_file(f"workspace/agents/{your_role}/{today}.md", daily_log)
```

---

## Quick Commands

```python
# Find my assigned tasks
tasks = tm.list_tasks()
my_tasks = [t for t in tasks if '{your_role}' in t.assigned]

# Find tasks that mention me
mentions = tm.find_mentions('{your_role}')

# Get task details
task = tm.find_task('task-001')
print(task.title, task.status, task.assigned)

# Read task thread
for comment in task.thread:
    print(f"{comment['timestamp']} - {comment['agent']}: {comment['message']}")
```

---

## Shell Commands (Alternative)

```bash
# Find work
ls workspace/tasks/ready-to-build/

# Read task
cat workspace/tasks/in-progress/task-001.md

# Find mentions
grep -r "@engineer" workspace/tasks/

# Check notifications
cat workspace/notifications.md

# View activity
tail -20 workspace/activity.log

# Today's activity
grep $(date +%Y-%m-%d) workspace/activity.log
```

---

## Role-Specific Workflows

### PM Agent
```python
# 1. Pick up from inbox
task = tm.find_work('pm')
tm.assign_task(task.id, 'pm')
tm.move_task(task.id, 'in-discovery')

# 2. Research & write PRD
# ... research ...

# 3. Link PRD
tm.update_task(task.id, prd='docs/specs/feature.md')

# 4. Request approval
tm.add_comment(task.id, 'pm', '@human PRD ready for review')

# 5. After approval, hand to architect
tm.move_task(task.id, 'in-planning')
tm.assign_task(task.id, 'architect')
tm.add_comment(task.id, 'pm', '@architect PRD approved, please plan')
```

### Architect Agent
```python
# 1. Pick up from in-planning
task = tm.find_work('architect')

# 2. Read PRD
prd = read_file(task.prd)

# 3. Design & write plan
# ... design ...

# 4. Link plan
tm.update_task(task.id, plan='docs/plans/feature.md')

# 5. Request approval
tm.add_comment(task.id, 'architect', '@human Plan ready for review')

# 6. After approval, create subtasks & notify engineers
tm.move_task(task.id, 'ready-to-build')
tm.add_comment(task.id, 'architect', '@engineer Tasks ready to build')
```

### Engineer Agent
```python
# 1. Pick up from ready-to-build
task = tm.find_work('engineer')
tm.assign_task(task.id, 'engineer')
tm.move_task(task.id, 'in-progress')

# 2. Implement
# ... code ...

# 3. Create PR & update task
tm.update_task(task.id, pr='https://github.com/user/repo/pull/123')

# 4. Mark ready for testing
tm.move_task(task.id, 'ready-for-testing')
tm.add_comment(task.id, 'engineer', '@qa Ready for testing')
```

### QA Agent
```python
# 1. Pick up from ready-for-testing
task = tm.find_work('qa')
tm.assign_task(task.id, 'qa')
tm.move_task(task.id, 'in-qa')

# 2. Test
# ... test ...

# 3. If bugs found
tm.add_comment(task.id, 'qa', '@engineer Bug found: [description]')
tm.move_task(task.id, 'in-progress')

# 4. If all good
tm.move_task(task.id, 'ready-to-deploy')
tm.add_comment(task.id, 'qa', 'All tests passing. Ready for deployment.')
```

---

## Remember

✅ **Read WORKING.md FIRST** - Every single invocation
✅ **Update WORKING.md** - Before exiting
✅ **Log activities** - As they happen
✅ **Be specific** - In comments and logs
✅ **Subscribe to threads** - Happens automatically when you comment

---

**Everything is just files. Use Read, Write, Edit, Glob, Grep.**

No APIs. No authentication. No rate limits. Just the file system.
