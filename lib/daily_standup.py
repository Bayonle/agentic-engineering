"""
Daily Standup Generator

Creates end-of-day summary showing:
- Completed tasks
- In-progress tasks
- Blocked tasks
- Tasks needing review
- Key decisions/activities
"""

import os
from datetime import datetime
from typing import List, Dict
from task_manager import TaskManager, Task


class StandupGenerator:
    """Generates daily standup reports"""

    def __init__(self, workspace_dir: str = 'workspace'):
        self.workspace = workspace_dir
        self.task_manager = TaskManager(workspace_dir)
        self.activity_log = os.path.join(workspace_dir, 'activity.log')
        self.standup_file = os.path.join(workspace_dir, 'standup.md')

    def generate(self, date: str = None) -> str:
        """
        Generate standup report

        Args:
            date: Date in YYYY-MM-DD format (defaults to today)

        Returns:
            Standup report as markdown string
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        # Get all tasks
        all_tasks = self.task_manager.list_tasks()

        # Categorize tasks
        completed = self._completed_today(all_tasks, date)
        in_progress = self._in_progress(all_tasks)
        blocked = self._blocked(all_tasks)
        needs_review = self._needs_review(all_tasks)

        # Get key activities
        activities = self._key_activities(date)

        # Format report
        report = self._format_report(
            date,
            completed,
            in_progress,
            blocked,
            needs_review,
            activities
        )

        # Save to file
        with open(self.standup_file, 'w') as f:
            f.write(report)

        return report

    def _completed_today(self, tasks: List[Task], date: str) -> List[Task]:
        """Find tasks completed today"""
        completed = []

        for task in tasks:
            if task.status == 'deployed':
                # Check if updated today
                task_date = task.updated[:10]  # YYYY-MM-DD
                if task_date == date:
                    completed.append(task)

        return completed

    def _in_progress(self, tasks: List[Task]) -> List[Task]:
        """Find tasks currently in progress"""
        return [
            t for t in tasks
            if t.status in ['in-progress', 'in-qa', 'in-discovery', 'in-planning']
        ]

    def _blocked(self, tasks: List[Task]) -> List[Task]:
        """Find blocked tasks"""
        return [t for t in tasks if t.status == 'blocked']

    def _needs_review(self, tasks: List[Task]) -> List[Task]:
        """Find tasks needing review"""
        return [t for t in tasks if t.status == 'ready-to-deploy']

    def _key_activities(self, date: str) -> List[str]:
        """Extract key activities from today's log"""
        if not os.path.exists(self.activity_log):
            return []

        with open(self.activity_log, 'r') as f:
            lines = f.readlines()

        # Filter to today
        today_lines = [line for line in lines if line.startswith(date)]

        # Extract key activities (skip heartbeats and routine stuff)
        key_activities = []
        skip_patterns = ['heartbeat', 'checking for work', 'polling']

        for line in today_lines:
            # Format: TIMESTAMP | AGENT | MESSAGE
            parts = line.strip().split(' | ', 2)
            if len(parts) == 3:
                message = parts[2]

                # Skip routine activities
                if any(pattern in message.lower() for pattern in skip_patterns):
                    continue

                key_activities.append(message)

        return key_activities

    def _format_report(
        self,
        date: str,
        completed: List[Task],
        in_progress: List[Task],
        blocked: List[Task],
        needs_review: List[Task],
        activities: List[str]
    ) -> str:
        """Format standup report as markdown"""

        lines = [
            f"# 📊 Daily Standup — {date}",
            ""
        ]

        # Completed
        if completed:
            lines.append("## ✅ Completed Today")
            lines.append("")
            for task in completed:
                assignee = ", ".join(task.assigned) if task.assigned else "unassigned"
                lines.append(f"- **{task.title}** ({assignee})")
            lines.append("")
        else:
            lines.append("## ✅ Completed Today")
            lines.append("")
            lines.append("- No tasks completed today")
            lines.append("")

        # In Progress
        if in_progress:
            lines.append("## 🔄 In Progress")
            lines.append("")
            for task in in_progress:
                assignee = ", ".join(task.assigned) if task.assigned else "unassigned"
                lines.append(f"- **{task.title}** — {task.status} ({assignee})")
            lines.append("")
        else:
            lines.append("## 🔄 In Progress")
            lines.append("")
            lines.append("- No tasks in progress")
            lines.append("")

        # Blocked
        if blocked:
            lines.append("## 🚫 Blocked")
            lines.append("")
            for task in blocked:
                assignee = ", ".join(task.assigned) if task.assigned else "unassigned"
                lines.append(f"- **{task.title}** ({assignee})")
                # Try to extract blocker from comments
                if task.thread:
                    last_comment = task.thread[-1]['message']
                    if len(last_comment) < 100:
                        lines.append(f"  - Blocker: {last_comment}")
            lines.append("")

        # Needs Review
        if needs_review:
            lines.append("## 👀 Needs Review")
            lines.append("")
            for task in needs_review:
                lines.append(f"- **{task.title}**")
                lines.append(f"  - Ready for deployment approval")
            lines.append("")

        # Key Activities
        if activities:
            lines.append("## 📝 Key Activities")
            lines.append("")
            # Show up to 10 most recent
            for activity in activities[-10:]:
                lines.append(f"- {activity}")
            lines.append("")

        # Summary stats
        lines.append("## 📈 Summary")
        lines.append("")
        lines.append(f"- Completed: {len(completed)}")
        lines.append(f"- In Progress: {len(in_progress)}")
        lines.append(f"- Blocked: {len(blocked)}")
        lines.append(f"- Needs Review: {len(needs_review)}")
        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append("")
        lines.append("View tasks: `ls workspace/tasks/*/`")
        lines.append("View activity: `tail -f workspace/activity.log`")

        return "\n".join(lines)


def generate_standup(workspace_dir: str = 'workspace', date: str = None) -> str:
    """Generate daily standup report"""
    generator = StandupGenerator(workspace_dir)
    return generator.generate(date)


if __name__ == '__main__':
    # Can be run as standalone script or cron job
    import sys

    workspace = sys.argv[1] if len(sys.argv) > 1 else 'workspace'
    date = sys.argv[2] if len(sys.argv) > 2 else None

    report = generate_standup(workspace, date)
    print(report)
