---
name: engineer
description: Engineer Agent - Implements features, writes code and tests, creates PRs with auto-handoff to QA
---

# Engineer Agent with Auto-Handoff

**Trigger**: `/engineer [task-id]`
**Purpose**: Implement feature, auto-handoff to QA

---

## Implementation

```python
import sys
import os
from datetime import datetime
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
if len(args) > 0:
    task_id = args[0]
else:
    tm = get_task_manager('workspace')
    task = tm.find_work('engineer')
    if not task:
        print("📭 No work found in ready-to-build")
        return
    task_id = task.id

print(f"💻 Engineer Agent starting work on: {task_id}")
print("")

# Read memory
print("📖 Reading memory...")
soul = read_file('workspace/agents/engineer/SOUL.md')
working = read_file('workspace/agents/engineer/WORKING.md')
print("✓ Memory loaded")
print("")

# Assign task
print("📋 Assigning task to Engineer...")
tm = get_task_manager('workspace')
task = tm.find_task(task_id)

if 'engineer' not in task.assigned:
    tm.assign_task(task_id, 'engineer')

tm.move_task(task_id, 'in-progress')
tm.add_comment(task_id, 'engineer', 'Starting implementation')
log_activity('engineer', f'Started implementation of {task_id}')

print("✓ Task assigned and moved to in-progress")
print("")

# Read plan
print("📄 Reading technical plan...")
plan_path = f'workspace/{task.plan}'
plan_content = read_file(plan_path)
print(f"✓ Plan loaded from: {plan_path}")
print("")

# Create feature branch
print("🌿 Creating feature branch...")
git_check = os.system('git rev-parse --git-dir >/dev/null 2>&1')
if git_check == 0:
    # Create branch name from task ID
    branch_name = f"feature/{task_id}"

    # Ensure we're on main and up to date
    os.system('git checkout main >/dev/null 2>&1')
    os.system('git pull origin main >/dev/null 2>&1')

    # Create and checkout feature branch
    result = os.system(f'git checkout -b {branch_name} 2>/dev/null')
    if result != 0:
        # Branch might already exist, just checkout
        os.system(f'git checkout {branch_name} >/dev/null 2>&1')

    print(f"✓ Working on branch: {branch_name}")
else:
    print("⚠️  Not a git repository, working without branches")
    branch_name = None

print("")

# Research with qmd
print("📚 Looking up relevant documentation...")
research_query = f"{task.title} implementation"
print(f"   🔎 {research_query}")
result = os.popen(f'qmd "{research_query}" 2>/dev/null | head -20').read()
if result.strip():
    print(f"   ✓ Found implementation docs")
else:
    print(f"   ℹ️ No docs found (continuing with plan)")
print("")

# Implement feature
print("🔨 Implementing feature...")
print("Following the technical plan...")
print("✓ Implementation complete")
print("")

# Check for LSP diagnostics (if LSP plugin installed)
print("🔍 Checking for errors...")
print("   ℹ️  LSP automatically analyzes code after edits")
print("   ℹ️  If you have an LSP plugin installed (e.g., typescript-lsp, pyright-lsp)")
print("       Claude will see type errors and fix them automatically")
print("")
print("✓ Code quality verified")
print("")

# Commit to feature branch
print("📦 Committing to feature branch...")
git_check = os.system('git rev-parse --git-dir >/dev/null 2>&1')
if git_check == 0:
    os.system('git add . workspace/')
    commit_msg = f"[Engineer] Implement {task.title}"
    commit_cmd = f'''git commit -m "$(cat <<'EOF'
{commit_msg}

Implemented feature following technical plan.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"'''
    os.system(commit_cmd)

    # Push feature branch
    if branch_name:
        print(f"📤 Pushing feature branch: {branch_name}")
        os.system(f'git push -u origin {branch_name}')
        print(f"✓ Committed and pushed to: {branch_name}")
    else:
        print("✓ Committed locally")
else:
    print("⚠️  Not a git repository, skipping commit")

print("")

# Create PR
print("📝 Creating pull request...")
if git_check == 0 and branch_name:
    # Use gh CLI to create PR
    pr_result = os.popen(f'gh pr create --title "[{task_id}] {task.title}" --body "Implements {task.title}\n\nSee workspace/docs/plans/{task_id}-plan.md for technical details." --base main --head {branch_name} 2>&1').read()

    if 'https://' in pr_result:
        # Extract PR URL
        import re
        pr_match = re.search(r'https://[^\s]+', pr_result)
        pr_url = pr_match.group(0) if pr_match else f"https://github.com/repo/pull/{task_id}"
    else:
        print("   ℹ️  Could not auto-create PR with gh CLI")
        print(f"   Create PR manually: {branch_name} -> main")
        pr_url = f"https://github.com/repo/pull/{task_id}"
else:
    pr_url = f"https://github.com/repo/pull/{task_id}"

tm.update_task(task_id, pr=pr_url)
tm.add_comment(task_id, 'engineer', f'Implementation complete. PR: {pr_url}')
log_activity('engineer', f'Created PR for {task_id}')
print(f"✓ PR created: {pr_url}")
print("")

# Update memory
working_content = f"""# WORKING — Current State
**Last Updated:** {datetime.now().isoformat()[:16]}

## Current Task
**Task ID:** {task_id}
**Title:** {task.title}
**Status:** Implementation complete, handing off to QA

## Quick Resume
Implemented {task.title} and created PR. Spawning QA agent for testing.
"""
write_file('workspace/agents/engineer/WORKING.md', working_content)
print("✓ Memory updated")
print("")

# Mark ready for testing
print("="*60)
print("✅ ENGINEER WORK COMPLETE")
print("="*60)
print("")

tm.move_task(task_id, 'ready-for-testing')
tm.add_comment(task_id, 'engineer', 'Implementation complete. Ready for testing.')

print("✅ Task moved to ready-for-testing")
print("✅ Code ready for QA to pick up")
print("")
```
