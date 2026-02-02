# Autonomous Agent Workspace

**File-system based task coordination for AI agent teams**

This workspace uses simple markdown files and directories to coordinate an autonomous team of AI agents. No external services, no APIs, no complexity — just files, git, and standard Unix tools.

---

## Quick Start

### 1. Initialize Git

```bash
cd workspace
git init
git add .
git commit -m "Initialize autonomous agent workspace"
```

### 2. Create Your First Task

```python
# In Claude Code or Python
from agents.src.task_manager import create_task

task = create_task(
    title="Build user authentication",
    description="Implement JWT-based authentication with 2FA support",
    priority="P1",
    tags=["backend", "security"]
)

print(f"Created: {task.id}")
# Task is now in workspace/tasks/inbox/
```

### 3. Agent Picks Up Task

When PM agent wakes up:
1. Reads `agents/pm/WORKING.md` (current state)
2. Checks `notifications.md` (any @mentions?)
3. Finds task in `tasks/inbox/`
4. Assigns to self, moves to `tasks/in-discovery/`
5. Starts working

---

## Directory Structure

```
workspace/
├── tasks/                      # Tasks organized by status
│   ├── inbox/                  # New, unassigned
│   ├── in-discovery/           # PM researching
│   ├── in-planning/            # Architect designing
│   ├── ready-to-build/         # For engineers
│   ├── in-progress/            # Being implemented
│   ├── ready-for-testing/      # For QA
│   ├── in-qa/                  # Testing
│   ├── ready-to-deploy/        # For DevOps
│   ├── deployed/               # Done
│   └── blocked/                # Stuck
│
├── agents/                     # Agent memory & personality
│   ├── pm/
│   │   ├── SOUL.md            # Who I am
│   │   ├── WORKING.md         # What I'm doing now
│   │   ├── 2026-02-02.md      # Today's log
│   │   ├── CONTEXT.md         # Long-term memory
│   │   └── subscriptions.json # Task subscriptions
│   ├── architect/
│   ├── engineer/
│   ├── qa/
│   ├── security/
│   └── devops/
│
├── docs/
│   ├── specs/                  # PRDs
│   ├── plans/                  # Technical plans
│   └── solutions/              # Learnings
│
├── activity.log                # Global activity feed
├── notifications.md            # Agent notifications
└── standup.md                  # Daily summary
```

---

## Task File Format

Tasks are markdown files with YAML frontmatter:

```markdown
---
id: task-001
title: Build user authentication
status: in-progress
priority: P1
created: 2026-02-02T10:00:00Z
updated: 2026-02-02T14:30:00Z
assigned: ["engineer"]
subscribers: ["pm", "architect", "engineer", "security"]
tags: ["backend", "security"]
prd: docs/specs/authentication.md
plan: docs/plans/authentication.md
pr: https://github.com/user/repo/pull/123
---

# Build user authentication

## Description
Implement JWT-based authentication with 2FA support...

## Thread

### 2026-02-02T10:00 - pm
Created task. @architect please plan this.

### 2026-02-02T12:00 - architect
Technical plan complete. See docs/plans/authentication.md

### 2026-02-02T14:30 - engineer
Implementation started. PR created.
```

---

## Agent Memory System

### SOUL.md — Personality

Who the agent is, their voice, what they care about. Read once on first invocation or when updated.

```markdown
# SOUL — Engineer Agent

**Personality:** Pragmatic craftsperson

**Voice:** Direct, specific, evidence-based

**What I care about:**
- Working code over perfect design
- Tests aren't optional
- Follow existing patterns
```

### WORKING.md — Current State

**Most important file.** Read FIRST on every invocation.

```markdown
# WORKING — Current State

## Current Task
**Task ID:** task-001
**Status:** Implementing auth API

## Progress
- [x] Created endpoints
- [ ] Writing tests
- [ ] Security scan

## Next Steps
1. Finish unit tests
2. Run security scan
3. Create PR

## Quick Resume
Implementing JWT auth API. Endpoints done, need to finish tests and run security scan before PR.
```

### Daily Log (YYYY-MM-DD.md)

Activity log for the day. Append throughout the day.

```markdown
# Daily Log — 2026-02-02

## 10:00 - Started auth implementation
Created API endpoints for login, register, 2FA.

## 14:30 - Tests written
All unit tests passing. Need integration tests.

## 16:00 - PR created
Security scan clean. Ready for review.
```

### CONTEXT.md — Long-Term Memory

Curated important information that should persist.

```markdown
# CONTEXT — Long-Term Memory

## Key Decisions
- Using JWT with 15min access tokens
- TOTP for 2FA (not SMS)

## Patterns Learned
- Always add rate limiting on auth endpoints
- Store JWT secret in env, never hardcode

## Important Facts
- User model has preferences field
- Redis used for session storage
```

---

## Common Operations

### Create Task

```python
from agents.src.task_manager import create_task

task = create_task("Build feature X", "Description...")
```

### Move Task

```python
from agents.src.task_manager import get_task_manager

tm = get_task_manager()
tm.move_task("task-001", "in-progress")
```

### Add Comment

```python
from agents.src.task_manager import add_comment

add_comment("task-001", "engineer", "@security Can you review?")
```

### Find Work

```python
from agents.src.task_manager import get_task_manager

tm = get_task_manager()
task = tm.find_work("engineer")  # Finds work for engineer
```

### Log Activity

```python
from agents.src.activity import log_activity

log_activity("engineer", "Completed auth API implementation")
```

### Send Notification

```python
from agents.src.notifications import notify

notify(
    to_agent="security",
    from_agent="engineer",
    message="Can you review the JWT implementation?",
    task_id="task-001"
)
```

### Check Notifications

```python
from agents.src.notifications import check_notifications

notifs = check_notifications("security")
for notif in notifs:
    print(f"{notif['from']}: {notif['message']}")
```

### Generate Standup

```python
from agents.src.daily_standup import generate_standup

report = generate_standup()
print(report)
```

Or via command line:
```bash
python agents/src/daily_standup.py workspace
```

---

## Agent Workflow

### On Startup (Every Invocation)

**1. Read Memory**
```python
# Read SOUL.md (who am I?)
soul = read_file("workspace/agents/{agent}/SOUL.md")

# Read WORKING.md (what am I doing?)
working = read_file("workspace/agents/{agent}/WORKING.md")

# Read today's log (what happened today?)
today = read_file(f"workspace/agents/{agent}/{date}.md")
```

**2. Check for Work**
```python
# Check notifications
from agents.src.notifications import check_notifications
notifs = check_notifications(agent_name)

# Check assigned tasks
from agents.src.task_manager import get_task_manager
tm = get_task_manager()
task = tm.find_work(agent_role)
```

**3. Do Work or Report Status**
```python
if task or notifs:
    # Do the work
    work_on_task(task)
else:
    # No work
    log_activity(agent_name, "No work found, standing by")
```

**4. Update Memory**
```python
# Update WORKING.md with current state
update_working_md()

# Append to today's log
append_to_daily_log()
```

---

## Search & Discovery

```bash
# Find all mentions of engineer
grep -r "@engineer" tasks/

# Find blocked tasks
grep -r "status: blocked" tasks/

# Find auth-related tasks
rg "authentication" tasks/

# What's ready to test?
ls tasks/ready-for-testing/

# Today's activity
grep "2026-02-02" activity.log

# Engineer's activity
grep "engineer" activity.log
```

---

## Git Workflow

Everything is in git. Full history, full visibility.

```bash
# See what changed today
git diff HEAD~1

# See task history
git log tasks/in-progress/task-001.md

# Who worked on this task?
git blame tasks/deployed/task-001.md

# What did engineer do this week?
git log --author="engineer" --since="1 week ago"
```

---

## Daily Standup

Run at end of day:

```bash
python agents/src/daily_standup.py
cat workspace/standup.md
```

Or add to cron:
```cron
0 23 * * * cd /path/to/project && python agents/src/daily_standup.py && cat workspace/standup.md | mail -s "Daily Standup" you@example.com
```

---

## Advantages Over ClickUp

| Feature | ClickUp | File System |
|---------|---------|-------------|
| **Setup** | API keys, config | `mkdir workspace` |
| **Read task** | API call | `cat task.md` |
| **Search** | API limits | `grep`, `rg`, `find` |
| **History** | Audit log | `git log` |
| **Offline** | ❌ No | ✅ Yes |
| **Latency** | ~100ms | <1ms |
| **Cost** | Free tier limits | ✅ Free |
| **Portability** | Locked in | ✅ Just files |
| **Debuggable** | Opaque | ✅ Transparent |

---

## Tips & Best Practices

**For Agents:**
- Read WORKING.md FIRST every time
- Update WORKING.md before exiting
- Log activities as they happen
- Be specific in comments
- Subscribe to threads you care about

**For Humans:**
- Use git to track all changes
- Review standup.md daily
- Check activity.log for real-time updates
- Use grep/rg for powerful search
- Trust the file system

**For Teams:**
- One workspace per project
- Git for collaboration
- Each agent has distinct SOUL
- Memory is in files, not "mental notes"

---

## Troubleshooting

**Task not moving?**
```bash
# Check task status
cat tasks/in-progress/task-001.md | grep "status:"

# Check who's assigned
cat tasks/in-progress/task-001.md | grep "assigned:"

# Check recent activity
tail activity.log
```

**Agent forgot context?**
```bash
# Check their WORKING.md
cat workspace/agents/engineer/WORKING.md

# Did they update it?
git log workspace/agents/engineer/WORKING.md
```

**Where is task-001?**
```bash
# Search all directories
find workspace/tasks -name "task-001.md"

# Or use grep
grep -r "^id: task-001" workspace/tasks/
```

---

## Next Steps

1. **Read Agent SOULs** - Understand each agent's personality
2. **Create First Task** - Use task_manager.py
3. **Run Agents** - Invoke agent skills in Claude Code
4. **Monitor Activity** - `tail -f workspace/activity.log`
5. **Generate Standup** - See daily progress

---

## Resources

- **Task Manager**: `agents/src/task_manager.py`
- **Activity Logger**: `agents/src/activity.py`
- **Notifications**: `agents/src/notifications.py`
- **Standup Generator**: `agents/src/daily_standup.py`
- **Agent SOULs**: `workspace/agents/*/SOUL.md`
- **System Design**: `AUTONOMOUS_AGENT_SYSTEM.md`

---

**Simple. Transparent. Git-based. Agent-native.**

Welcome to your autonomous agent workspace. 🚀
