"""
Task Manager - File System Based Task Coordination

Replaces ClickUp with a simple, transparent file-system approach.
Tasks are markdown files in status-based directories.
"""

import os
import re
import glob
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
import json


@dataclass
class Task:
    """Represents a task in the autonomous agent system"""
    id: str
    title: str
    description: str
    status: str = 'inbox'
    priority: str = 'P2'
    assigned: List[str] = field(default_factory=list)
    subscribers: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    updated: str = field(default_factory=lambda: datetime.now().isoformat())
    prd: Optional[str] = None
    plan: Optional[str] = None
    pr: Optional[str] = None
    thread: List[Dict[str, str]] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert task to markdown format"""
        # Frontmatter
        frontmatter = {
            'id': self.id,
            'title': self.title,
            'status': self.status,
            'priority': self.priority,
            'created': self.created,
            'updated': self.updated,
            'assigned': self.assigned,
            'subscribers': self.subscribers,
            'tags': self.tags,
        }

        if self.prd:
            frontmatter['prd'] = self.prd
        if self.plan:
            frontmatter['plan'] = self.plan
        if self.pr:
            frontmatter['pr'] = self.pr

        # Convert to YAML-like format
        fm_lines = ['---']
        for key, value in frontmatter.items():
            if isinstance(value, list):
                fm_lines.append(f'{key}: {json.dumps(value)}')
            else:
                fm_lines.append(f'{key}: {value}')
        fm_lines.append('---')

        # Body
        body = [
            '',
            f'# {self.title}',
            '',
            '## Description',
            self.description,
            ''
        ]

        # Thread
        if self.thread:
            body.append('## Thread')
            body.append('')
            for comment in self.thread:
                body.append(f"### {comment['timestamp']} - {comment['agent']}")
                body.append(comment['message'])
                body.append('')

        return '\n'.join(fm_lines + body)

    @classmethod
    def from_markdown(cls, filepath: str) -> 'Task':
        """Parse markdown file into Task object"""
        with open(filepath, 'r') as f:
            content = f.read()

        # Parse frontmatter
        fm_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if not fm_match:
            raise ValueError(f"Invalid task file format: {filepath}")

        fm_text, body = fm_match.groups()

        # Parse frontmatter fields
        frontmatter = {}
        for line in fm_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Parse JSON arrays
                if value.startswith('['):
                    frontmatter[key] = json.loads(value)
                else:
                    frontmatter[key] = value

        # Parse thread from body
        thread = []
        thread_section = re.search(r'## Thread\n\n(.*)$', body, re.DOTALL)
        if thread_section:
            thread_text = thread_section.group(1)
            comments = re.findall(
                r'### ([\d\-:T]+) - ([^\n]+)\n(.*?)(?=\n### |\Z)',
                thread_text,
                re.DOTALL
            )
            for timestamp, agent, message in comments:
                thread.append({
                    'timestamp': timestamp,
                    'agent': agent,
                    'message': message.strip()
                })

        # Extract description
        desc_match = re.search(r'## Description\n(.*?)(?=\n## |\Z)', body, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ''

        return cls(
            id=frontmatter.get('id', ''),
            title=frontmatter.get('title', ''),
            description=description,
            status=frontmatter.get('status', 'inbox'),
            priority=frontmatter.get('priority', 'P2'),
            assigned=frontmatter.get('assigned', []),
            subscribers=frontmatter.get('subscribers', []),
            tags=frontmatter.get('tags', []),
            created=frontmatter.get('created', ''),
            updated=frontmatter.get('updated', ''),
            prd=frontmatter.get('prd'),
            plan=frontmatter.get('plan'),
            pr=frontmatter.get('pr'),
            thread=thread
        )


class TaskManager:
    """
    Manages tasks in the file system

    Tasks are stored as markdown files in status-based directories:
    workspace/tasks/{status}/{task-id}.md
    """

    def __init__(self, workspace_dir: str = 'workspace'):
        self.workspace = workspace_dir
        self.tasks_dir = os.path.join(workspace_dir, 'tasks')
        self.activity_log = os.path.join(workspace_dir, 'activity.log')

        # Valid status directories
        self.statuses = [
            'inbox',
            'in-discovery',
            'in-planning',
            'ready-to-build',
            'in-progress',
            'ready-for-testing',
            'in-qa',
            'ready-to-deploy',
            'deployed',
            'blocked'
        ]

    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        # Find highest existing ID
        max_id = 0
        for status in self.statuses:
            status_dir = os.path.join(self.tasks_dir, status)
            if os.path.exists(status_dir):
                for filename in os.listdir(status_dir):
                    if filename.startswith('task-') and filename.endswith('.md'):
                        try:
                            num = int(filename[5:8])  # task-XXX.md
                            max_id = max(max_id, num)
                        except ValueError:
                            continue

        return f"task-{max_id + 1:03d}"

    def create_task(
        self,
        title: str,
        description: str,
        priority: str = 'P2',
        tags: List[str] = None
    ) -> Task:
        """Create a new task in inbox"""
        task_id = self._generate_task_id()

        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags or []
        )

        # Write to inbox
        filepath = os.path.join(self.tasks_dir, 'inbox', f'{task_id}.md')
        with open(filepath, 'w') as f:
            f.write(task.to_markdown())

        # Log activity
        self.log_activity('system', f"Created task {task_id}: {title}")

        return task

    def find_task(self, task_id: str) -> Optional[Task]:
        """Find task by ID across all status directories"""
        for status in self.statuses:
            filepath = os.path.join(self.tasks_dir, status, f'{task_id}.md')
            if os.path.exists(filepath):
                return Task.from_markdown(filepath)
        return None

    def _find_task_file(self, task_id: str) -> Optional[str]:
        """Find task file path by ID"""
        for status in self.statuses:
            filepath = os.path.join(self.tasks_dir, status, f'{task_id}.md')
            if os.path.exists(filepath):
                return filepath
        return None

    def update_task(self, task_id: str, **updates) -> Task:
        """Update task fields"""
        filepath = self._find_task_file(task_id)
        if not filepath:
            raise ValueError(f"Task {task_id} not found")

        task = Task.from_markdown(filepath)

        # Update fields
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        # Update timestamp
        task.updated = datetime.now().isoformat()

        # Write back
        with open(filepath, 'w') as f:
            f.write(task.to_markdown())

        return task

    def move_task(self, task_id: str, new_status: str) -> Task:
        """Move task to new status directory"""
        if new_status not in self.statuses:
            raise ValueError(f"Invalid status: {new_status}")

        old_filepath = self._find_task_file(task_id)
        if not old_filepath:
            raise ValueError(f"Task {task_id} not found")

        task = Task.from_markdown(old_filepath)
        old_status = task.status

        # Update status
        task.status = new_status
        task.updated = datetime.now().isoformat()

        # Write to new location
        new_filepath = os.path.join(self.tasks_dir, new_status, f'{task_id}.md')
        with open(new_filepath, 'w') as f:
            f.write(task.to_markdown())

        # Remove old file
        os.remove(old_filepath)

        # Log activity
        self.log_activity('system', f"Moved {task_id} from {old_status} to {new_status}")

        return task

    def add_comment(self, task_id: str, agent: str, message: str) -> Task:
        """Add comment to task thread"""
        filepath = self._find_task_file(task_id)
        if not filepath:
            raise ValueError(f"Task {task_id} not found")

        task = Task.from_markdown(filepath)

        # Add comment
        comment = {
            'timestamp': datetime.now().isoformat()[:16],  # YYYY-MM-DDTHH:MM
            'agent': agent,
            'message': message
        }
        task.thread.append(comment)

        # Auto-subscribe commenter
        if agent not in task.subscribers:
            task.subscribers.append(agent)

        # Update timestamp
        task.updated = datetime.now().isoformat()

        # Write back
        with open(filepath, 'w') as f:
            f.write(task.to_markdown())

        # Log activity
        self.log_activity(agent, f"Commented on {task_id}")

        # Notify subscribers
        self._notify_subscribers(task, agent, message)

        return task

    def assign_task(self, task_id: str, agent: str) -> Task:
        """Assign task to agent"""
        task = self.find_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if agent not in task.assigned:
            task.assigned.append(agent)

            # Auto-subscribe
            if agent not in task.subscribers:
                task.subscribers.append(agent)

        # Update
        return self.update_task(
            task_id,
            assigned=task.assigned,
            subscribers=task.subscribers
        )

    def find_work(self, agent_role: str) -> Optional[Task]:
        """Find work for agent based on their role"""
        # Check assigned tasks first
        for status in self.statuses:
            status_dir = os.path.join(self.tasks_dir, status)
            if not os.path.exists(status_dir):
                continue

            for filename in os.listdir(status_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(status_dir, filename)
                    task = Task.from_markdown(filepath)

                    if agent_role in task.assigned:
                        return task

        # Check for mentions
        mentions = self.find_mentions(agent_role)
        if mentions:
            return mentions[0]

        # Check appropriate status directory
        status_map = {
            'pm': 'inbox',
            'architect': 'in-planning',
            'engineer': 'ready-to-build',
            'qa': 'ready-for-testing',
            'security': 'in-progress',  # Reviews ongoing work
            'devops': 'ready-to-deploy'
        }

        target_status = status_map.get(agent_role)
        if not target_status:
            return None

        status_dir = os.path.join(self.tasks_dir, target_status)
        if not os.path.exists(status_dir):
            return None

        # Find unassigned task
        for filename in os.listdir(status_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(status_dir, filename)
                task = Task.from_markdown(filepath)

                if not task.assigned:
                    return task

        return None

    def find_mentions(self, agent: str) -> List[Task]:
        """Find tasks where agent is mentioned"""
        mentions = []
        pattern = f"@{agent}"

        for status in self.statuses:
            status_dir = os.path.join(self.tasks_dir, status)
            if not os.path.exists(status_dir):
                continue

            for filename in os.listdir(status_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(status_dir, filename)

                    with open(filepath, 'r') as f:
                        content = f.read()

                    if pattern in content:
                        task = Task.from_markdown(filepath)
                        mentions.append(task)

        return mentions

    def list_tasks(self, status: Optional[str] = None) -> List[Task]:
        """List all tasks, optionally filtered by status"""
        tasks = []

        statuses_to_check = [status] if status else self.statuses

        for s in statuses_to_check:
            status_dir = os.path.join(self.tasks_dir, s)
            if not os.path.exists(status_dir):
                continue

            for filename in os.listdir(status_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(status_dir, filename)
                    task = Task.from_markdown(filepath)
                    tasks.append(task)

        return tasks

    def log_activity(self, agent: str, message: str):
        """Log activity to activity feed"""
        timestamp = datetime.now().isoformat()
        log_line = f"{timestamp} | {agent} | {message}\n"

        with open(self.activity_log, 'a') as f:
            f.write(log_line)

    def _notify_subscribers(self, task: Task, commenter: str, message: str):
        """Add notifications for task subscribers"""
        notifications_file = os.path.join(self.workspace, 'notifications.md')

        # Don't notify the commenter
        to_notify = [s for s in task.subscribers if s != commenter]

        if not to_notify:
            return

        # Read existing notifications
        if os.path.exists(notifications_file):
            with open(notifications_file, 'r') as f:
                content = f.read()
        else:
            content = "# Notifications\n\n## Pending\n\n"

        # Add new notifications
        for agent in to_notify:
            notif = f"""
### @{agent}
From: {commenter} ({task.id})
Message: {message[:100]}{"..." if len(message) > 100 else ""}
Time: {datetime.now().isoformat()[:16]}
Link: workspace/tasks/{task.status}/{task.id}.md

"""
            # Insert after "## Pending"
            content = content.replace("## Pending\n\n", f"## Pending\n\n{notif}")

        with open(notifications_file, 'w') as f:
            f.write(content)


# Convenience functions

def get_task_manager(workspace_dir: str = 'workspace') -> TaskManager:
    """Get TaskManager instance"""
    return TaskManager(workspace_dir)


def create_task(title: str, description: str, **kwargs) -> Task:
    """Quick task creation"""
    tm = get_task_manager()
    return tm.create_task(title, description, **kwargs)


def find_task(task_id: str) -> Optional[Task]:
    """Quick task lookup"""
    tm = get_task_manager()
    return tm.find_task(task_id)


def add_comment(task_id: str, agent: str, message: str) -> Task:
    """Quick comment addition"""
    tm = get_task_manager()
    return tm.add_comment(task_id, agent, message)
