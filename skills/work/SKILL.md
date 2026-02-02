---
name: work
description: Smart workflow orchestrator - spawns agents in fresh background contexts
---

# Workflow Orchestrator

**Trigger**: `/work task-id`

## CRITICAL: How This Skill Works

This skill provides **instructions for Claude** to orchestrate agents. When invoked:

1. Claude reads task status from filesystem
2. Claude determines which agent should run next
3. **Claude uses the ACTUAL Task tool** to spawn that agent in background
4. Claude exits immediately (orchestrator done)
5. User resumes later with `/work task-id`

**THIS IS NOT PYTHON CODE THAT RUNS - IT'S INSTRUCTIONS FOR CLAUDE TO FOLLOW**

---

## Step 1: Read Task Status

When `/work {task-id}` is invoked, Claude should:

1. Read the task file: `workspace/tasks/*/{task-id}.md`
2. Extract the current status
3. If task not found, tell user and stop

```
Read workspace/tasks/inbox/{task-id}.md
  OR workspace/tasks/in-planning/{task-id}.md
  OR workspace/tasks/ready-to-build/{task-id}.md
  OR etc...
```

---

## Step 2: Determine Next Agent

Map status to agent:

| Task Status | Next Agent | What They Do |
|-------------|------------|--------------|
| `inbox` | PM | Write PRD |
| `in-discovery` | PM | Continue PRD |
| `in-planning` | Architect | Write technical plan |
| `ready-to-build` | Engineer | Implement code |
| `in-progress` | Engineer | Continue implementation |
| `ready-for-testing` | QA | Test feature |
| `in-qa` | QA | Continue testing |
| `ready-to-deploy` | DevOps | Deploy to production |
| `deployed` | NONE | Workflow complete! |

---

## Step 3: SPAWN AGENT (Use Task Tool)

**THIS IS THE CRITICAL PART - Claude must use the actual Task tool**

After determining the next agent, Claude should invoke the Task tool like this:

### For PM Agent:
```
Use Task tool with:
  subagent_type: "general-purpose"
  description: "PM agent writes PRD for {task-id}"
  run_in_background: true
  prompt: |
    You are the PM agent. Work in the current directory.

    Execute: /pm {task-id}

    Do your work, commit, and exit. The orchestrator will spawn the next agent.
```

### For Architect Agent:
```
Use Task tool with:
  subagent_type: "general-purpose"
  description: "Architect designs solution for {task-id}"
  run_in_background: true
  prompt: |
    You are the Architect agent. Work in the current directory.

    Execute: /architect {task-id}

    Do your work, commit, and exit. The orchestrator will spawn the next agent.
```

### For Engineer Agent:
```
Use Task tool with:
  subagent_type: "general-purpose"
  description: "Engineer implements {task-id}"
  run_in_background: true
  prompt: |
    You are the Engineer agent. Work in the current directory.

    Execute: /engineer {task-id}

    Do your work, commit, and exit. The orchestrator will spawn the next agent.
```

### For QA Agent:
```
Use Task tool with:
  subagent_type: "general-purpose"
  description: "QA tests {task-id}"
  run_in_background: true
  prompt: |
    You are the QA agent. Work in the current directory.

    Execute: /qa {task-id}

    Do your work, commit, and exit. The orchestrator will spawn the next agent.
```

### For DevOps Agent:
```
Use Task tool with:
  subagent_type: "general-purpose"
  description: "DevOps deploys {task-id}"
  run_in_background: true
  prompt: |
    You are the DevOps agent. Work in the current directory.

    Execute: /deploy {task-id}

    Do your work and commit. This is the final phase.
```

---

## Step 4: Exit Immediately

After spawning the agent, Claude should:

1. Tell the user the agent was spawned
2. Provide monitoring commands
3. **STOP** - do not wait, do not continue

Example response:
```
✅ Spawned PM agent in background for task-001

Monitor progress:
  tail -f workspace/activity.log
  cat workspace/agents/pm/WORKING.md

Resume workflow after approval:
  /work task-001
```

---

## Workflow Pattern

```
User: /work task-001

Claude:
  1. Reads task status → "inbox"
  2. Determines next agent → PM
  3. Uses Task tool (run_in_background=true) → Spawns PM
  4. Tells user: "PM spawned, monitor with..."
  5. DONE (exits, context freed)

[PM works in fresh background context]
[PM finishes, updates files, exits]

User: /work task-001

Claude:
  1. Reads task status → "in-planning"
  2. Determines next agent → Architect
  3. Uses Task tool → Spawns Architect
  4. Tells user: "Architect spawned..."
  5. DONE

[Repeat until deployed]
```

---

## Why This Pattern?

**Fresh Context Each Time:**
- Orchestrator: ~1KB context (just reads status, spawns, exits)
- Each agent: Fresh ~10KB context (reads only what it needs)
- No accumulation, no hallucinations

**Resume Capable:**
- User can stop anytime
- Run `/work task-id` to continue
- Status read from filesystem, not memory

**Scalable:**
- Works for 100+ step workflows
- Each step is isolated

---

## Common Mistakes to Avoid

❌ **Don't**: Write Python code that calls `use_task_tool()` - that function doesn't exist
❌ **Don't**: Wait for the agent to complete - spawn and exit immediately
❌ **Don't**: Keep context open while agent works - that defeats the purpose
❌ **Don't**: Try to chain agents within one context

✅ **Do**: Use the actual Task tool that Claude has access to
✅ **Do**: Set `run_in_background: true`
✅ **Do**: Exit immediately after spawning
✅ **Do**: Let user resume with `/work task-id`

---

## Monitoring Commands

After spawning an agent, tell the user:

```bash
# Watch all activity
tail -f workspace/activity.log

# Check specific agent
cat workspace/agents/pm/WORKING.md
cat workspace/agents/architect/WORKING.md
cat workspace/agents/engineer/WORKING.md
cat workspace/agents/qa/WORKING.md
cat workspace/agents/devops/WORKING.md

# Check task status
ls workspace/tasks/*/

# Resume workflow
/work {task-id}
```
