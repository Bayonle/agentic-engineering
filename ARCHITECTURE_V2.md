# Architecture V2: Fresh Context Per Agent

## Problem with Current Design

Current: Agents try to spawn each other from within skills
- ❌ Creates long context chains
- ❌ Risk of hallucination
- ❌ Can't resume if interrupted
- ❌ Skills can't directly call Task tool

## New Architecture

### Option 1: Smart Orchestrator (Recommended)

**`/work` orchestrator** spawns each agent in sequence, each in fresh context:

```python
# /work skill becomes:
/work task-001

→ Spawns PM in background with Task tool
→ Waits for PM to complete (monitors WORKING.md)
→ Spawns Architect in background
→ Waits for Architect
→ Spawns Engineer in background
→ etc.
```

**Benefits:**
- ✅ Each agent in fresh context
- ✅ Central coordination
- ✅ Easy to monitor progress
- ✅ Can resume workflow

### Option 2: Event-Driven (Advanced)

Agents signal completion, orchestrator listens:

```python
# Each agent just does work and exits
PM completes → writes "completed" to WORKING.md

# Orchestrator watches files
while not workflow_complete:
    check task status
    if phase complete:
        spawn next agent
```

## Proposed Implementation

### 1. Individual Agent Skills (No Handoff)

Each skill just does its work:

```python
# /pm skill
def pm_agent():
    # Do PM work
    write_prd()
    update_working_md(status="completed")
    # EXIT - don't spawn next agent
```

### 2. Smart /work Orchestrator

```python
# /work skill
def workflow_orchestrator(task_id):
    phases = [
        ('pm', 'inbox', 'in-planning'),
        ('architect', 'in-planning', 'ready-to-build'),
        ('engineer', 'ready-to-build', 'ready-for-testing'),
        ('qa', 'ready-for-testing', 'ready-to-deploy'),
        ('deploy', 'ready-to-deploy', 'deployed')
    ]

    for agent, from_status, to_status in phases:
        print(f"Starting {agent} phase...")

        # Spawn agent in background with Task tool
        spawn_agent_in_background(agent, task_id)

        # Wait for completion (check WORKING.md)
        wait_for_agent_completion(agent, task_id)

        # Verify status moved
        assert task_status == to_status

        print(f"{agent} complete!")

    print("Workflow complete!")
```

### 3. Resume Capability

```python
# /work can resume from last completed phase
def resume_workflow(task_id):
    current_status = get_task_status(task_id)

    # Find where to resume
    phase_map = {
        'inbox': 'pm',
        'in-planning': 'architect',
        'ready-to-build': 'engineer',
        'ready-for-testing': 'qa',
        'ready-to-deploy': 'deploy'
    }

    resume_agent = phase_map[current_status]
    print(f"Resuming from {resume_agent} phase...")
```

## Agent Communication

Agents communicate **only via filesystem**:

```
workspace/
├── tasks/{status}/{task-id}.md    # Task state
├── agents/{agent}/WORKING.md      # Agent state
├── docs/specs/{task-id}-prd.md    # PM output
├── docs/plans/{task-id}-plan.md   # Architect output
└── activity.log                   # Audit trail
```

## Context Management

Each agent invocation:
- ✅ Fresh context (< 10k tokens)
- ✅ Reads only what it needs from files
- ✅ Writes output to files
- ✅ Updates WORKING.md before exit
- ✅ Exits (conversation ends)

## Implementation Plan

1. **Phase 1**: Remove auto-handoff from individual skills
2. **Phase 2**: Make /work orchestrator spawn agents properly
3. **Phase 3**: Add progress monitoring
4. **Phase 4**: Add resume capability
5. **Phase 5**: Add error handling

## Example: Proper /work Execution

```bash
/work task-001

# Orchestrator:
→ "Spawning PM agent in background..."
→ [Task tool spawns PM] ← Fresh context
→ PM reads task, writes PRD, updates WORKING.md, exits
→ [Orchestrator checks: PRD created? ✓]
→ "Spawning Architect agent in background..."
→ [Task tool spawns Architect] ← Fresh context
→ Architect reads PRD, writes plan, exits
→ [Orchestrator checks: Plan created? ✓]
→ ... continues ...
```

## Benefits

1. **Scalability**: Can handle long-running tasks
2. **Quality**: Each agent has fresh context
3. **Reliability**: Can resume if interrupted
4. **Monitoring**: Clear progress tracking
5. **Debugging**: Easy to see where failures occur

## Next Steps

Want me to implement this architecture?
