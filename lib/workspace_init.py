"""
Workspace initialization - shared utility for finding/creating workspace
"""
from pathlib import Path
import shutil
import sys

def find_project_root():
    """
    Find the project root by looking for:
    1. Existing workspace/ directory (walk up tree)
    2. .git directory (project root)
    3. Fall back to current directory
    """
    current = Path.cwd().resolve()

    # Walk up the directory tree
    for parent in [current] + list(current.parents):
        # Check for existing workspace
        if (parent / 'workspace').exists():
            return parent

        # Check for .git (project root)
        if (parent / '.git').exists():
            return parent

        # Don't go above home directory
        if parent == Path.home():
            break

    # Fall back to current directory
    return current

def get_plugin_dir():
    """Find the plugin directory"""
    # Try multiple locations
    locations = [
        Path.home() / '.claude/plugins/cache/agentic-workflow',
        Path.home() / '.claude/plugins/agentic-workflow',
        Path(__file__).resolve().parent.parent if '__file__' in globals() else None
    ]

    for loc in locations:
        if loc and loc.exists():
            return loc

    # Fallback
    return Path.home() / '.claude/plugins/agentic-workflow'

def ensure_workspace(plugin_dir=None):
    """
    Initialize workspace in project root if it doesn't exist
    Returns: (project_root, workspace_path)
    """
    if plugin_dir is None:
        plugin_dir = get_plugin_dir()

    # Find project root
    project_root = find_project_root()
    workspace = project_root / 'workspace'

    if workspace.exists():
        return project_root, workspace

    print("📦 First time setup: Creating agentic workspace...")
    print(f"   Project root: {project_root}")
    print("")

    # Copy template
    template = plugin_dir / 'lib/templates/workspace'

    if template.exists():
        shutil.copytree(template, workspace)
        print("✅ Workspace created from template")
    else:
        # Create minimal workspace
        print("⚠️  Template not found, creating minimal workspace...")

        dirs = [
            'agents/pm', 'agents/architect', 'agents/engineer',
            'agents/qa', 'agents/devops',
            'tasks/inbox', 'tasks/in-discovery', 'tasks/in-planning',
            'tasks/ready-to-build', 'tasks/in-progress',
            'tasks/ready-for-testing', 'tasks/in-qa',
            'tasks/ready-to-deploy', 'tasks/deployed',
            'docs/specs', 'docs/plans', 'docs/qa-reports',
            'docs/deployment-reports'
        ]

        for d in dirs:
            (workspace / d).mkdir(parents=True, exist_ok=True)

        # Create minimal SOUL and WORKING files for each agent
        agents = ['pm', 'architect', 'engineer', 'qa', 'devops']

        for agent in agents:
            agent_dir = workspace / f'agents/{agent}'
            agent_dir.mkdir(parents=True, exist_ok=True)

            # Create minimal SOUL.md
            soul_file = agent_dir / 'SOUL.md'
            if not soul_file.exists():
                soul_file.write_text(f"""# SOUL — {agent.upper()} Agent

**Role:** {agent.capitalize()}

Read the full agent definition from: agents/{agent}-agent.md

This file contains your personality, guidelines, and persistent memory.
Update it as you learn things that should persist across sessions.
""")

            # Create minimal WORKING.md
            working_file = agent_dir / 'WORKING.md'
            if not working_file.exists():
                working_file.write_text(f"""# WORKING — Current State

**Last Updated:** (never)

## Current Task
None

## Progress
(No work started)

## Next Steps
1. Wait for task assignment
""")

        # Create empty activity log
        (workspace / 'activity.log').touch()

        # Create notifications file
        notifications_file = workspace / 'notifications.md'
        notifications_file.write_text("""# Notifications

## Pending

(No notifications)

## Delivered

(No delivered notifications)
""")

        print("✅ Minimal workspace created")

    print(f"   Location: {workspace}")
    print("")
    print("Workspace structure:")
    print("  workspace/")
    print("    ├── agents/        # Agent memory (SOUL, WORKING)")
    print("    ├── tasks/         # Task management")
    print("    └── docs/          # PRDs, plans, reports")
    print("")

    return project_root, workspace
