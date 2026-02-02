# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-02-02

### MAJOR REWRITE - True Fresh Context Architecture

**Problem Solved**: Previous versions had fake Python code that pretended to spawn agents but actually ran everything in the same context, causing context bloat and hallucinations.

**Solution**: Complete rewrite of all skills as pure **instructions for Claude** rather than Python code. The orchestrator now properly uses the actual Task tool to spawn agents in background.

### Changed - All Skill Files Rewritten

- **skills/work/SKILL.md**: Now pure instructions telling Claude to:
  1. Read task status from filesystem
  2. Determine next agent
  3. **Use actual Task tool** with `run_in_background=true`
  4. Exit immediately

- **skills/pm/SKILL.md**: Instruction-based, no fake handoff code
- **skills/architect/SKILL.md**: Instruction-based, no fake handoff code
- **skills/engineer/SKILL.md**: Instruction-based, no fake handoff code
- **skills/qa/SKILL.md**: Instruction-based, no fake handoff code
- **skills/deploy/SKILL.md**: Instruction-based, final agent

### How It Works Now

```
User: /work task-001

Claude:
  1. Reads: workspace/tasks/inbox/task-001.md
  2. Determines: next agent = PM
  3. Uses Task tool: spawn PM in background
  4. Says: "PM spawned, monitor with tail -f..."
  5. EXITS (context freed, ~1KB used)

[PM runs in FRESH background context]
[PM finishes, updates files, exits]

User: /work task-001

Claude:
  1. Reads: workspace/tasks/in-planning/task-001.md
  2. Determines: next agent = Architect
  3. Uses Task tool: spawn Architect in background
  4. EXITS (context freed)

[Repeat until deployed]
```

### Key Principles

1. **Skills are INSTRUCTIONS, not code**
   - Skills tell Claude what to do
   - Claude uses its actual tools (Read, Write, Bash, Task)
   - No fake `use_task_tool()` functions

2. **Orchestrator spawns and exits**
   - `/work` reads status, spawns agent, exits
   - User resumes with `/work task-id`
   - Each invocation is ~1KB context

3. **Agents do work and exit**
   - Each agent reads what it needs
   - Does its work
   - Commits to git
   - Updates status
   - Exits (doesn't spawn next agent)

4. **Communication via filesystem only**
   - Task status in workspace/tasks/
   - Agent memory in workspace/agents/
   - Documents in workspace/docs/
   - No context sharing between agents

### Benefits

✅ **Scalable**: 100+ step workflows without context bloat
✅ **No hallucinations**: Each agent has fresh 10KB context
✅ **Resumable**: Stop/start anytime, filesystem is truth
✅ **Traceable**: Complete audit trail in files
✅ **Debuggable**: Clear separation between agents

### Migration

No migration needed. Just update the plugin and run `/work task-id`.

## [1.2.3] - 2026-02-02

### Added
- **UI/Browser Testing with agent-browser** - QA agent now uses agent-browser CLI
- Automated screenshot capture during testing
- Visual regression verification
- UI element presence checking
- Screenshots saved to `workspace/docs/qa-reports/screenshots/`
- Screenshots included in test reports
- Support for interactive browser testing (click, fill, navigate, extract)

### Changed
- QA SKILL.md: Added agent-browser UI testing workflow
- QA SOUL.md: Added UI testing step with agent-browser commands
- Test reports now include UI/Browser Testing section
- Test summary table includes UI test results
- README: Added agent-browser installation and usage guide

### Benefits
✅ Automated UI verification without manual checking
✅ Visual regression detection
✅ Screenshots as evidence in test reports
✅ Interactive testing capabilities
✅ Better coverage of frontend changes

### Requirements (Optional)
```bash
npm install -g @vercel/agent-browser
```

## [1.2.2] - 2026-02-02

### Fixed - CRITICAL
- **Engineer now uses feature branches** instead of working directly on main
- Creates `feature/{task-id}` branch before starting work
- Ensures main is up to date before branching
- Commits and pushes to feature branch
- Creates PR from feature branch to main
- Uses `gh pr create` if available for automatic PR creation

### Changed
- Engineer SKILL.md: Added feature branch creation and proper git workflow
- Engineer SOUL.md: Added "Git Workflow - CRITICAL" section
- Workflow steps renumbered to include branching step
- Emphasized: "NEVER WORK ON MAIN DIRECTLY"

### Why This Matters
- Main branch stays stable
- Enables proper code review via PRs
- Multiple features can be developed in parallel
- Easy rollback if needed
- Follows industry best practices

## [1.2.1] - 2026-02-02

### Added
- **Comprehensive Test Reports**: QA agent now generates detailed test reports
- Test report saved to `workspace/docs/qa-reports/{task-id}-test-report.md`
- Includes test summary with pass/fail/skip counts
- Quality gates metrics (coverage, performance, security)
- Issues found with severity levels
- Performance metrics and security review
- Deployment recommendation with sign-off
- Test report linked in git commit messages

### Changed
- QA SOUL.md updated with test report generation instructions
- QA approval comments now include test report location
- Git commits now reference test report with metrics

## [1.2.0] - 2026-02-02

### Changed - MAJOR ARCHITECTURE REDESIGN
- **Fresh Context Architecture**: Each agent now runs in isolated background context
- Removed fake auto-handoff code from individual agent skills
- Agents now just do their work and exit cleanly
- `/work` orchestrator properly uses Task tool to spawn agents in background
- Eliminates context bloat and hallucinations in long-running workflows
- Supports resume capability - can pick up from any phase

### Added
- Smart orchestrator in `/work` skill that spawns agents via Task tool
- Phase detection based on filesystem state
- Resume capability by reading task status
- Proper background agent spawning with `run_in_background=True`
- Complete monitoring instructions for tracking agent progress

### Fixed
- Context chain issues causing hallucinations in long workflows
- Agents no longer try to spawn next agent from same context
- Removed non-functional `use_task_tool()` calls from skills
- Proper separation of concerns between orchestrator and agents

### Benefits
- ✅ Scalable: Handles 100+ step workflows without context issues
- ✅ Quality: Each agent gets fresh context for better accuracy
- ✅ Reliable: Can resume from any phase if interrupted
- ✅ Traceable: Complete file-based audit trail
- ✅ Clean: Agents communicate only via filesystem

## [1.1.0] - 2026-02-02

### Added
- Quick task creation with `/task` command
- Auto-incrementing task IDs
- Status auto-determination based on agent assignment
- Workspace initialization utility (`lib/workspace_init.py`)

### Fixed
- Duplicate workspace creation in subdirectories
- Project root detection now walks up directory tree
- Always works from project root, not current directory

## [1.0.0] - 2026-02-02

### Added
- Initial release of Agentic Workflow plugin
- PM Agent with requirements research and PRD writing
- Architect Agent with solution design and planning
- Engineer Agent with code implementation
- QA Agent with testing and quality verification
- DevOps Agent with deployment automation
- Full workflow orchestrator (`/work` command)
- Auto-workspace initialization on first use
- Git commit integration for all agent phases
- qmd CLI integration for documentation search
- File-based task management system
- Agent memory system (SOUL.md, WORKING.md)
- Auto-handoff between agents
- Human approval gates (PRD, Plan, Deployment)
- Comprehensive README and documentation

### Features
- Zero per-project setup required
- Works in any directory
- Automatic workspace creation
- Git commits with proper attribution
- Documentation research during agent work
- Complete SDLC automation
- Plugin-based distribution

## [Unreleased]

### Planned
- Slack/Discord notifications
- CI/CD platform integrations
- Custom agent roles
- Team collaboration features
- Analytics and metrics
- Multi-language support
