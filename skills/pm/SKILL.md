---
name: pm
description: PM Agent - Researches requirements, writes PRDs, manages product discovery and requirements gathering with auto-handoff to Architect
---

# Product Manager Agent with Auto-Handoff

**Trigger**: `/pm [task-id]`
**Purpose**: Research, write PRD, auto-handoff to Architect

---

## What This Does

1. Auto-initialize workspace (first time only)
2. Read memory (SOUL.md, WORKING.md)
3. Pick up task from inbox
4. Research requirements (with qmd if available)
5. Write comprehensive PRD
6. Request human approval
7. Git commit (if enabled)
8. **Auto-spawn Architect when approved**

---

## Implementation

```python
import sys
import os
import time
from datetime import datetime
from pathlib import Path
import shutil

# ============================================================================
# PLUGIN INITIALIZATION - Auto-setup workspace
# ============================================================================

def get_plugin_dir():
    """Find the plugin directory"""
    # When running as a skill, __file__ is available
    if '__file__' in globals():
        skill_file = Path(__file__).resolve()
        return skill_file.parent.parent.parent  # skills/pm/SKILL.md -> plugin root
    # Fallback to standard location
    return Path.home() / '.claude/plugins/cache/agentic-workflow'

def ensure_workspace():
    """Initialize workspace in current project if it doesn't exist"""
    cwd = Path.cwd()
    workspace = cwd / 'workspace'

    if workspace.exists():
        return workspace

    print("📦 First time setup: Creating agentic workspace...")
    print("")

    # Get plugin directory
    plugin_dir = get_plugin_dir()
    template = plugin_dir / 'lib/templates/workspace'

    if template.exists():
        # Copy full template
        shutil.copytree(template, workspace)
        print("✅ Workspace created from template")
    else:
        # Create minimal workspace structure
        print("⚠️  Template not found, creating minimal workspace...")

        # Create directory structure
        dirs = [
            'agents/pm', 'agents/architect', 'agents/engineer', 'agents/qa', 'agents/devops',
            'tasks/inbox', 'tasks/in-discovery', 'tasks/in-planning',
            'tasks/ready-to-build', 'tasks/in-progress',
            'tasks/ready-for-testing', 'tasks/in-qa',
            'tasks/ready-to-deploy', 'tasks/deployed',
            'docs/specs', 'docs/plans', 'docs/qa-reports', 'docs/deployment-reports'
        ]

        for d in dirs:
            (workspace / d).mkdir(parents=True, exist_ok=True)

        # Copy SOUL templates from plugin assets
        soul_mapping = {
            'pm': 'pm', 'architect': 'architect', 'engineer': 'engineer',
            'qa': 'qa', 'devops': 'deploy'
        }

        for agent, skill_name in soul_mapping.items():
            soul_template = plugin_dir / f'skills/{skill_name}/assets/SOUL.md'
            if soul_template.exists():
                shutil.copy(soul_template, workspace / f'agents/{agent}/SOUL.md')

        # Create empty activity log
        (workspace / 'activity.log').touch()

        print("✅ Minimal workspace created")

    print(f"   Location: {workspace}")
    print("")
    print("Workspace structure:")
    print("  workspace/")
    print("    ├── agents/        # Agent memory (SOUL, WORKING)")
    print("    ├── tasks/         # Task management")
    print("    └── docs/          # PRDs, plans, reports")
    print("")

    return workspace

# Initialize plugin
PLUGIN_DIR = get_plugin_dir()
LIB_DIR = PLUGIN_DIR / 'lib'
sys.path.insert(0, str(LIB_DIR))

# Ensure workspace exists
workspace = ensure_workspace()
project_root = workspace.parent

# Import after path is set
from task_manager import get_task_manager
from activity import log_activity

# ============================================================================
# PM AGENT LOGIC
# ============================================================================

# Get task ID from args or find work
if len(args) > 0:
    task_id = args[0]
else:
    # Find work
    tm = get_task_manager('workspace')
    task = tm.find_work('pm')
    if not task:
        print("📭 No work found in inbox")
        print("")
        print("Create a task with:")
        print(f"  echo 'Task description' > workspace/tasks/inbox/task-001.md")
        return
    task_id = task.id

print(f"🤖 PM Agent starting work on: {task_id}")
print("")

# Step 1: Read Memory
print("📖 Reading memory...")
soul = read_file('workspace/agents/pm/SOUL.md')
working = read_file('workspace/agents/pm/WORKING.md')
print("✓ Memory loaded")
print("")

# Step 2: Assign task
print("📋 Assigning task to PM...")
tm = get_task_manager('workspace')
task = tm.find_task(task_id)

tm.assign_task(task_id, 'pm')
tm.move_task(task_id, 'in-discovery')
tm.add_comment(task_id, 'pm', f'Starting discovery phase for: {task.title}')
log_activity('pm', f'Started discovery on {task_id}')

print(f"✓ Task assigned and moved to in-discovery")
print("")

# Step 3: Research Requirements
print("🔍 Researching requirements...")
print(f"   Task: {task.title}")
print(f"   Description: {task.description}")
print("")

# Use qmd for quick documentation research
print("📚 Searching documentation with qmd...")
research_queries = [
    f"{task.title} best practices",
    f"{task.title} security considerations"
]

for query in research_queries[:1]:  # Just do one quick search
    print(f"   🔎 {query}")
    result = os.popen(f'qmd "{query}" 2>/dev/null | head -20').read()
    if result.strip():
        print(f"   ✓ Found relevant docs")
    else:
        print(f"   ℹ️  No docs found (qmd may not be installed)")
    break

print("")
print("✓ Research complete")
print("")

# Step 4: Write PRD
print("📝 Writing PRD...")

prd_filename = f"{task_id}-prd.md"
prd_content = f"""---
feature: {task.title}
status: draft
created: {datetime.now().strftime('%Y-%m-%d')}
author: PM Agent
task_id: {task_id}
priority: {task.priority}
---

# {task.title}

## Problem Statement

{task.description}

## User Stories

### Story 1: User wants to {task.title.lower()}
**As a** user
**I want** to {task.title.lower()}
**So that** I can achieve the goal

**Acceptance Criteria:**
- [ ] Feature works as described
- [ ] Error handling is in place
- [ ] Tests are written
- [ ] Documentation is updated

## Functional Requirements

### Must Have (P0)
1. Core functionality as described in problem statement
2. Basic error handling
3. User feedback on success/failure

### Should Have (P1)
1. Input validation
2. Comprehensive error messages

## Non-Functional Requirements

### Performance
- Response time < 2 seconds for typical operations

### Security
- Input sanitization
- Authentication/authorization as needed
- Follow OWASP best practices

### Usability
- Clear user feedback
- Intuitive interface

## Technical Considerations
- Use existing patterns in codebase
- Follow language/framework conventions
- Best practices for the technology stack

## Edge Cases & Error Handling
1. **Invalid input**: Validate and return clear error message
2. **Network failure**: Retry with exponential backoff
3. **Concurrent access**: Handle with appropriate locking

## Dependencies
- **External**: None identified yet
- **Internal**: Existing project infrastructure

## Out of Scope
- Advanced features not in initial requirements
- Performance optimization (future iteration)

## Success Metrics
- Feature deployed without incidents
- User acceptance criteria met
- Code review approved

## Open Questions
- Any specific performance requirements?
- Special security considerations?
"""

write_file(f'workspace/docs/specs/{prd_filename}', prd_content)

tm.update_task(task_id, prd=f'docs/specs/{prd_filename}')
tm.add_comment(task_id, 'pm', f'PRD created: workspace/docs/specs/{prd_filename}')
log_activity('pm', f'Created PRD for {task_id}')

print(f"✓ PRD written to: workspace/docs/specs/{prd_filename}")
print("")

# Step 5: Request Approval
print("👤 Requesting human approval...")
tm.add_comment(
    task_id,
    'pm',
    f"""@human PRD ready for review

**PRD Location**: workspace/docs/specs/{prd_filename}

Please review and approve to proceed with technical planning.

**To approve**: Add comment with "approved" or "PRD approved"
**To request changes**: Add comment with your feedback
"""
)

print("")
print("="*60)
print("⏸️  WAITING FOR HUMAN APPROVAL")
print("="*60)
print("")
print(f"📄 Review PRD: cat workspace/docs/specs/{prd_filename}")
print("")
print("Approve with:")
print(f'  python3 << \'EOF\'')
print(f'  import sys')
print(f'  sys.path.append("workspace/../{LIB_DIR}")')
print(f'  from task_manager import get_task_manager')
print(f'  tm = get_task_manager("workspace")')
print(f'  tm.add_comment("{task_id}", "human", "PRD approved!")')
print(f'  EOF')
print("")
print("Or just tell Claude: 'I approve the PRD for {task_id}'")
print("")

# Step 6: Poll for Approval
print("⏳ Polling for approval (checking every 5 minutes)...")
print("")

approved = False
while not approved:
    task = tm.find_task(task_id)

    # Check recent comments for approval
    if task.thread:
        recent_comments = task.thread[-5:]  # Last 5 comments
        for comment in recent_comments:
            if comment['agent'] == 'human':
                message = comment['message'].lower()
                if 'approve' in message or 'approved' in message:
                    if 'prd' in message or 'approved!' in message:
                        approved = True
                        print("✅ PRD APPROVED!")
                        break

    if not approved:
        print(f"⏳ Still waiting... (checked {datetime.now().strftime('%H:%M')})")
        time.sleep(300)  # 5 minutes

print("")

# Step 7: Update Memory
print("💾 Updating memory...")

working_content = f"""# WORKING — Current State

**Last Updated:** {datetime.now().isoformat()[:16]}

---

## Current Task

**Task ID:** {task_id}
**Title:** {task.title}
**Status:** PRD approved, handing off to Architect

## Progress
- [x] Found task in inbox
- [x] Assigned to self
- [x] Moved to in-discovery
- [x] Researched requirements
- [x] Wrote PRD
- [x] Received approval
- [ ] Hand off to architect

## Quick Resume
PRD approved for {task.title}. Spawning Architect agent for technical planning.
"""

write_file('workspace/agents/pm/WORKING.md', working_content)
log_activity('pm', f'PRD approved for {task_id}, handing off to architect')

print("✓ Memory updated")
print("")

# Step 8: Git Commit
print("📦 Committing work to git...")

# Check if git is available
git_check = os.system('git rev-parse --git-dir >/dev/null 2>&1')
if git_check == 0:
    # Stage PM's files
    os.system('git add workspace/docs/specs/ workspace/agents/pm/WORKING.md workspace/tasks/')

    # Create commit with agent attribution
    commit_msg = f"[PM] Create PRD for {task.title}"
    commit_cmd = f'''git commit -m "$(cat <<'EOF'
{commit_msg}

Created PRD: workspace/docs/specs/{prd_filename}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"'''
    os.system(commit_cmd)

    # Push to remote
    os.system('git push')

    log_activity('pm', f'Committed and pushed: {commit_msg}')
    print(f"✓ Committed: {commit_msg}")
else:
    log_activity('pm', 'WARNING: Not a git repository, skipping commit')
    print("⚠️  Not a git repository, skipping commit")

print("")

# Step 9: AUTO-HANDOFF to Architect
print("="*60)
print("🚀 AUTO-HANDOFF TO ARCHITECT")
print("="*60)
print("")

# Move task to planning
tm.move_task(task_id, 'in-planning')
tm.assign_task(task_id, 'architect')
tm.add_comment(task_id, 'pm', '@architect PRD approved. Please create technical plan.')

print("Spawning Architect agent in background (FRESH CONTEXT)...")
print("")

# Use Task tool to spawn Architect
use_task_tool(
    subagent_type="general-purpose",
    description=f"Architect designs implementation for {task_id}",
    prompt=f"""
You are the Architect agent working on task {task_id}.

IMPORTANT: Stay in current directory (project already set up):
Current directory has agentic workspace ready.

Execute the architect skill with auto-handoff:
/architect {task_id}

The /architect skill has auto-handoff built in.
""",
    run_in_background=True
)

print("✅ PM work complete!")
print(f"✅ Architect agent spawned in background")
print("")
print("Next: Architect will design solution and request your approval")
print("")
print("Monitor: tail -f workspace/activity.log")
```
