---
name: work
description: Orchestrator - Runs full SDLC workflow from PM through deployment. Coordinates all agents automatically.
---

# Full Workflow Orchestrator

**Trigger**: `/work [task-id]`
**Purpose**: Run complete workflow - PM → Architect → Engineer → QA → DevOps

---

## What This Does

Executes the full autonomous workflow:

1. **PM** - Researches and writes PRD
2. **Architect** - Designs solution and creates plan
3. **Engineer** - Implements code and creates PR
4. **QA** - Tests feature and requests deployment approval
5. **DevOps** - Deploys to production

Each agent auto-hands off to the next. You only need to approve at key gates (PRD, Plan, Deployment).

---

## Implementation

```python
import sys
import os
from pathlib import Path

# Plugin initialization
def get_plugin_dir():
    if '__file__' in globals():
        return Path(__file__).resolve().parent.parent.parent
    return Path.home() / '.claude/plugins/cache/agentic-workflow'

PLUGIN_DIR = get_plugin_dir()
sys.path.insert(0, str(PLUGIN_DIR / 'lib'))

from task_manager import get_task_manager
from activity import log_activity

# Get task ID
if len(args) == 0:
    print("❌ Task ID required")
    print("Usage: /work task-001")
    print("")
    print("Or create a new task:")
    print("  echo 'Feature description' > workspace/tasks/inbox/task-001.md")
    print("  /work task-001")
    return

task_id = args[0]

print("🚀 Starting full workflow for: {task_id}")
print("")
print("Workflow:")
print("  PM → Architect → Engineer → QA → DevOps")
print("")
print("You'll be asked to approve:")
print("  ✓ PRD (after PM)")
print("  ✓ Technical Plan (after Architect)")
print("  ✓ Deployment (after QA)")
print("")

# Log workflow start
log_activity('orchestrator', f'Starting full workflow for {task_id}')

# Invoke PM agent
print("="*60)
print("STEP 1: PM AGENT")
print("="*60)
print("")
print("PM will research requirements and write PRD...")
print("")

# Use the /pm skill
use_skill('pm', task_id)

print("")
print("Full workflow initiated!")
print("PM agent will:")
print("  1. Research requirements")
print("  2. Write PRD")
print("  3. Request your approval")
print("  4. Auto-spawn Architect (after approval)")
print("")
print("Each agent will auto-handoff to the next.")
print("Monitor progress: tail -f workspace/activity.log")
```
