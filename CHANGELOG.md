# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
