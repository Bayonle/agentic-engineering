---
name: architect
description: Architect Agent - Designs technical solutions, creates implementation plans, manages system architecture with auto-handoff to Engineer
---

# Architect Agent with Background Handoff

**Trigger**: `/architect [task-id]`
**Purpose**: Design technical solution, create plan, auto-handoff to Engineer

---

## Critical Instructions

**After human approves the plan:**

1. **Commit the plan to git** (architect's work)
2. **Use the Task tool** to spawn Engineer in background
3. **STOP executing** - do not continue engineer work here

---

## Architect Workflow

1. Read SOUL.md and WORKING.md
2. Read the approved PRD
3. Research patterns with qmd
4. Design technical solution
5. Write implementation plan
6. Request human approval
7. **When approved: Git commit, spawn Engineer, EXIT**

---

## Implementation

This skill provides guidance for Claude when acting as the Architect agent. Claude should:

1. **Initialize workspace** (if needed - plugin handles this)
2. **Read context:**
   - `workspace/agents/architect/SOUL.md`
   - `workspace/agents/architect/WORKING.md`
   - PRD from `workspace/docs/specs/`

3. **Research with qmd:**
   ```bash
   qmd "technical pattern for {feature}"
   qmd "architecture best practices {technology}"
   ```

4. **Design solution:**
   - High-level architecture
   - API contracts
   - Data models
   - Component structure
   - Security considerations
   - Testing strategy

5. **Write plan to:** `workspace/docs/plans/{task-id}-plan.md`

6. **Request approval:**
   ```python
   tm.add_comment(task_id, 'architect', '@human Plan ready for review')
   ```

7. **After approval, commit:**
   ```python
   # Check git
   git_check = os.system('git rev-parse --git-dir >/dev/null 2>&1')
   if git_check == 0:
       os.system('git add workspace/docs/plans/ workspace/agents/architect/')
       commit_msg = f"[Architect] Create technical plan for {task.title}"
       commit_cmd = f'''git commit -m "$(cat <<'EOF'
{commit_msg}

Created plan: workspace/docs/plans/{plan_filename}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"'''
       os.system(commit_cmd)
       os.system('git push')
   ```

8. **Spawn Engineer:**
   ```python
   use_task_tool(
       subagent_type="general-purpose",
       description=f"Engineer implements {task_id}",
       prompt=f"Execute /engineer {task_id}",
       run_in_background=True
   )
   ```

---

**Remember:** Fresh context for Engineer = separate background invocation!
