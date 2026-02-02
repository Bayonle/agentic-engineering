---
name: work
description: Smart workflow orchestrator that spawns each agent in fresh background context for scalable long-running tasks
---

# Smart Workflow Orchestrator

**Trigger**: `/work task-id`

This orchestrator coordinates the full SDLC by spawning each agent in a separate background process with fresh context.

---

## How It Works

When you invoke `/work task-001`, Claude will:

1. **Detect current phase** by reading task status from filesystem
2. **Spawn appropriate agent** in background via Task tool
3. **Monitor completion** by checking filesystem state
4. **Move to next phase** when complete
5. **Support resume** - can pick up from any phase

---

## Execution Instructions for Claude

When the user invokes `/work task-id`, execute this workflow:

### Phase 1: Detect Current Phase

Read the task file to determine where we are:

```python
import sys
from pathlib import Path

# Find plugin and add lib to path
if '__file__' in globals():
    plugin_dir = Path(__file__).resolve().parent.parent.parent
else:
    plugin_dir = Path.home() / '.claude/plugins/cache/agentic-workflow'

sys.path.insert(0, str(plugin_dir / 'lib'))
from task_manager import get_task_manager
from workspace_init import ensure_workspace

# Ensure workspace and get project root
project_root, workspace = ensure_workspace(plugin_dir)

# Get task
task_id = args[0] if len(args) > 0 else None
if not task_id:
    print("❌ Task ID required")
    print("Usage: /work task-001")
    return

tm = get_task_manager('workspace')
task = tm.find_task(task_id)

if not task:
    print(f"❌ Task {task_id} not found")
    return

print(f"🎯 Workflow Orchestrator for: {task_id}")
print(f"   Title: {task.title}")
print(f"   Current status: {task.status}")
print("")
```

### Phase 2: Determine Next Agent

Map status to agent:

```python
phase_map = {
    'inbox': 'pm',
    'in-discovery': 'pm',
    'in-planning': 'architect',
    'ready-to-build': 'engineer',
    'in-progress': 'engineer',
    'ready-for-testing': 'qa',
    'in-qa': 'qa',
    'ready-to-deploy': 'deploy',
    'deployed': None  # Complete!
}

next_agent = phase_map.get(task.status)

if next_agent is None:
    print("✅ Task already deployed!")
    print(f"   Status: {task.status}")
    return

print(f"📍 Next phase: {next_agent}")
print("")
```

### Phase 3: Spawn Agent in Background

Use the **Task tool** to spawn the agent:

```python
print("="*60)
print(f"🚀 SPAWNING {next_agent.upper()} AGENT IN BACKGROUND")
print("="*60)
print("")

# Build the prompt for the agent
agent_prompts = {
    'pm': f"""You are the PM agent working on task {task_id}.

The workspace is already set up in the current directory.

Execute: /pm {task_id}

This skill will:
1. Read the task from workspace/tasks/
2. Research and write the PRD
3. Request human approval
4. Commit the work
5. Exit (orchestrator handles next phase)
""",
    'architect': f"""You are the Architect agent working on task {task_id}.

The workspace is already set up in the current directory.

Execute: /architect {task_id}

This skill will:
1. Read the PRD from workspace/docs/specs/
2. Design the technical solution
3. Write the implementation plan
4. Request human approval
5. Commit the work
6. Exit (orchestrator handles next phase)
""",
    'engineer': f"""You are the Engineer agent working on task {task_id}.

The workspace is already set up in the current directory.

Execute: /engineer {task_id}

This skill will:
1. Read the plan from workspace/docs/plans/
2. Implement the feature
3. Write tests
4. Create PR
5. Commit the work
6. Exit (orchestrator handles next phase)
""",
    'qa': f"""You are the QA agent working on task {task_id}.

The workspace is already set up in the current directory.

Execute: /qa {task_id}

This skill will:
1. Read the implementation
2. Run tests
3. Request deployment approval
4. Commit the work
5. Exit (orchestrator handles next phase)
""",
    'deploy': f"""You are the DevOps agent working on task {task_id}.

The workspace is already set up in the current directory.

Execute: /deploy {task_id}

This skill will:
1. Deploy to production
2. Verify deployment
3. Mark task as deployed
4. Commit the work
5. Exit (workflow complete!)
"""
}

prompt = agent_prompts[next_agent]
```

**NOW USE THE TASK TOOL** (this is the critical part):

After determining the next agent and building the prompt, Claude should directly invoke the Task tool:

```
Task tool with parameters:
- subagent_type: "general-purpose"
- description: "{next_agent} works on task-{task_id}"
- prompt: {prompt from above}
- run_in_background: True
```

### Phase 4: Inform User

After spawning the agent:

```python
print(f"✅ {next_agent.capitalize()} agent spawned in background")
print("")
print("Monitor progress:")
print(f"  tail -f workspace/activity.log")
print(f"  cat workspace/agents/{next_agent}/WORKING.md")
print("")
print("Check task status:")
print(f"  cat workspace/tasks/*/{task_id}.md | grep 'status:'")
print("")
print("To resume workflow after approval:")
print(f"  /work {task_id}")
```

---

## Key Architecture Benefits

1. **Fresh Context**: Each agent spawned via Task tool starts with < 10k tokens
2. **File Communication**: Agents read/write workspace files only, no context sharing
3. **No Chaining**: Agents don't spawn each other, orchestrator manages flow
4. **Resume Capable**: Can restart from any phase by reading filesystem state
5. **Scalable**: Handles 100+ step workflows without context bloat
6. **Traceable**: Complete file-based audit trail

---

## Example Workflow

```bash
# User creates task
echo "Implement user authentication" > workspace/tasks/inbox/task-001.md

# Start workflow
/work task-001

# Orchestrator spawns PM in background (fresh context)
# PM writes PRD, requests approval, exits
# User approves PRD

# Resume workflow
/work task-001

# Orchestrator spawns Architect in background (fresh context)
# Architect writes plan, requests approval, exits
# User approves plan

# Resume workflow
/work task-001

# Orchestrator spawns Engineer in background (fresh context)
# Engineer implements, commits, exits

# Resume workflow
/work task-001

# Orchestrator spawns QA in background (fresh context)
# QA tests, requests deployment approval, exits
# User approves deployment

# Resume workflow
/work task-001

# Orchestrator spawns DevOps in background (fresh context)
# DevOps deploys, marks complete, exits

# Done!
/work task-001
# "✅ Task already deployed!"
```

---

## Monitoring

```bash
# Overall progress
tail -f workspace/activity.log

# Current phase
cat workspace/tasks/*/task-001.md | grep status

# Agent state
cat workspace/agents/pm/WORKING.md
cat workspace/agents/architect/WORKING.md
cat workspace/agents/engineer/WORKING.md
cat workspace/agents/qa/WORKING.md
cat workspace/agents/devops/WORKING.md
```

---

## Critical Implementation Notes for Claude

**DO:**
- Use the actual Task tool to spawn agents in background
- Pass `run_in_background=True` for scalability
- Read filesystem state to determine phase
- Let agents exit cleanly after their work

**DON'T:**
- Try to spawn agents from Python code in skills
- Chain agents in same conversation context
- Use fake `use_task_tool()` function
- Keep long-running context across phases

**The /work skill is instructions for YOU (Claude) to execute, not Python code to run!**
