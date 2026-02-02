---
name: work
description: Workflow orchestrator - spawns agents in fresh background contexts using Claude Code's native subagent system
---

# Workflow Orchestrator

**Trigger**: `/work task-id`

## Step 0: Ensure Workspace Exists

Before doing anything else, check if `workspace/` directory exists:

```bash
ls workspace/
```

**If workspace doesn't exist:**
1. Tell user: "No workspace found. Creating one..."
2. Copy from `lib/templates/workspace/` if available
3. Or create minimal structure with directories and empty files

The `/task` command also auto-creates workspace, so typically it will exist.

---

## How This Works

This skill instructs Claude to:
1. Read task status from filesystem
2. Determine which agent should run next
3. **Spawn that agent in background** using the Task tool
4. Exit immediately (orchestrator done)
5. User resumes later with `/work task-id`

## Available Subagents

This plugin provides proper Claude Code subagents in `agents/`:

| Agent | When Used | What It Does |
|-------|-----------|--------------|
| `pm-agent` | Task in `inbox` | Writes business-focused PRD |
| `architect-agent` | Task in `in-planning` | Creates technical plan |
| `engineer-agent` | Task in `ready-to-build` | Implements on feature branch |
| `qa-agent` | Task in `ready-for-testing` | Tests and generates report |
| `devops-agent` | Task in `ready-to-deploy` | Deploys to production |

---

## Step 1: Read Task Status

Check where the task is in the workflow:

```bash
# Find the task
ls workspace/tasks/*/task-{id}.md
```

Status locations:
- `workspace/tasks/inbox/` → PM
- `workspace/tasks/in-planning/` → Architect
- `workspace/tasks/ready-to-build/` → Engineer
- `workspace/tasks/ready-for-testing/` → QA
- `workspace/tasks/ready-to-deploy/` → DevOps
- `workspace/tasks/deployed/` → DONE!

---

## Step 2: Spawn the Right Agent

**Use the Task tool to spawn the appropriate subagent in background:**

### If task is in `inbox` → Spawn PM Agent

```
Task tool:
  subagent_type: "pm-agent"
  description: "PM writes PRD for {task-id}"
  run_in_background: true
  prompt: |
    Work on task {task-id}.

    1. Read the task from workspace/tasks/inbox/{task-id}.md
    2. Research the domain
    3. Write business-focused PRD to workspace/docs/specs/{task-id}-prd.md
    4. Request human approval
    5. After approval: commit, move task to in-planning, exit
```

### If task is in `in-planning` → Spawn Architect Agent

```
Task tool:
  subagent_type: "architect-agent"
  description: "Architect designs {task-id}"
  run_in_background: true
  prompt: |
    Work on task {task-id}.

    1. Read PRD from workspace/docs/specs/{task-id}-prd.md
    2. Design technical solution
    3. Write plan to workspace/docs/plans/{task-id}-plan.md
    4. Request human approval
    5. After approval: commit, move task to ready-to-build, exit
```

### If task is in `ready-to-build` → Spawn Engineer Agent

```
Task tool:
  subagent_type: "engineer-agent"
  description: "Engineer implements {task-id}"
  run_in_background: true
  prompt: |
    Work on task {task-id}.

    1. Create feature branch: feature/{task-id}
    2. Read plan from workspace/docs/plans/{task-id}-plan.md
    3. Implement the code
    4. Write tests
    5. Commit, push, create PR
    6. Move task to ready-for-testing, exit
```

### If task is in `ready-for-testing` → Spawn QA Agent

```
Task tool:
  subagent_type: "qa-agent"
  description: "QA tests {task-id}"
  run_in_background: true
  prompt: |
    Work on task {task-id}.

    1. Run tests
    2. Use agent-browser for UI testing if available
    3. Write test report to workspace/docs/qa-reports/{task-id}-test-report.md
    4. Request deployment approval
    5. After approval: commit, move task to ready-to-deploy, exit
```

### If task is in `ready-to-deploy` → Spawn DevOps Agent

```
Task tool:
  subagent_type: "devops-agent"
  description: "DevOps deploys {task-id}"
  run_in_background: true
  prompt: |
    Work on task {task-id}.

    1. Merge the PR
    2. Deploy to production
    3. Verify health
    4. Move task to deployed
    5. Exit - workflow complete!
```

### If task is in `deployed` → Done!

Tell user: "Task {task-id} is already deployed! 🎉"

---

## Step 3: Exit Immediately

After spawning the agent, tell the user:

```
✅ Spawned {agent} in background for {task-id}

The agent is working in a FRESH context.

Monitor progress:
  tail -f workspace/activity.log
  cat workspace/agents/{agent}/WORKING.md

Resume workflow after approval:
  /work {task-id}
```

**DO NOT WAIT for the agent. Just spawn and exit.**

---

## The Pattern

```
User: /work task-001
         ↓
Claude (main): Reads status → inbox
Claude (main): Spawns pm-agent in background
Claude (main): Says "PM spawned" and EXITS
         ↓
[pm-agent works in FRESH background context]
[pm-agent finishes, exits]
         ↓
User: /work task-001
         ↓
Claude (main): Reads status → in-planning
Claude (main): Spawns architect-agent in background
Claude (main): EXITS
         ↓
[Repeat until deployed]
```

---

## Why Background Subagents?

From Claude Code docs:
> "Background subagents run concurrently while you continue working."

Benefits:
- **Fresh context** - Each agent starts clean (~10KB not ~100KB)
- **No hallucinations** - Clean context prevents confusion
- **Resumable** - Can stop/start anytime
- **Parallel work** - User can do other things while agent works

---

## Key Points

1. **Subagents cannot spawn subagents** - Only main conversation can spawn
2. **Orchestrator spawns and exits** - Don't wait for agent to complete
3. **User resumes with /work** - Each invocation is fresh
4. **Filesystem is truth** - Agents communicate via files only

---

## Monitoring

```bash
# Watch activity
tail -f workspace/activity.log

# Check agent status
cat workspace/agents/pm/WORKING.md
cat workspace/agents/architect/WORKING.md
cat workspace/agents/engineer/WORKING.md
cat workspace/agents/qa/WORKING.md
cat workspace/agents/devops/WORKING.md

# Check task location
ls workspace/tasks/*/

# Resume workflow
/work {task-id}
```
