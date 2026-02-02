"""
Notification System

Manages @mentions and thread subscriptions.
Agents check notifications.md on startup to see what needs their attention.
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Optional
import json


class NotificationManager:
    """Manages agent notifications"""

    def __init__(self, workspace_dir: str = 'workspace'):
        self.workspace = workspace_dir
        self.notifications_file = os.path.join(workspace_dir, 'notifications.md')
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create notifications.md if it doesn't exist"""
        if not os.path.exists(self.notifications_file):
            with open(self.notifications_file, 'w') as f:
                f.write("# Notifications\n\n## Pending\n\n## Delivered\n\n")

    def add_notification(
        self,
        to_agent: str,
        from_agent: str,
        message: str,
        task_id: Optional[str] = None,
        link: Optional[str] = None
    ):
        """
        Add a notification for an agent

        Args:
            to_agent: Agent to notify
            from_agent: Agent sending notification
            message: Notification message
            task_id: Related task ID
            link: Link to relevant file/resource
        """
        with open(self.notifications_file, 'r') as f:
            content = f.read()

        # Create notification entry
        timestamp = datetime.now().isoformat()[:16]  # YYYY-MM-DDTHH:MM

        notif = f"""
### @{to_agent}
From: {from_agent}{f' ({task_id})' if task_id else ''}
Message: {message}
Time: {timestamp}
{f'Link: {link}' if link else ''}

"""

        # Insert after "## Pending"
        content = content.replace("## Pending\n\n", f"## Pending\n\n{notif}")

        with open(self.notifications_file, 'w') as f:
            f.write(content)

    def get_notifications(self, agent: str) -> List[Dict[str, str]]:
        """
        Get pending notifications for an agent

        Returns list of notification dicts:
        [
            {
                'from': 'engineer',
                'message': '...',
                'time': '2026-02-02T14:30',
                'task_id': 'task-001',
                'link': 'workspace/tasks/...'
            }
        ]
        """
        if not os.path.exists(self.notifications_file):
            return []

        with open(self.notifications_file, 'r') as f:
            content = f.read()

        # Extract pending section
        pending_match = re.search(
            r'## Pending\n\n(.*?)## Delivered',
            content,
            re.DOTALL
        )

        if not pending_match:
            return []

        pending_section = pending_match.group(1)

        # Find notifications for this agent
        pattern = rf'### @{agent}\n(.*?)(?=\n### @|\n## |\Z)'
        matches = re.findall(pattern, pending_section, re.DOTALL)

        notifications = []

        for match in matches:
            notif = {}

            # Parse fields
            from_match = re.search(r'From: ([^\n(]+)', match)
            if from_match:
                notif['from'] = from_match.group(1).strip()

            task_match = re.search(r'\(([^)]+)\)', match)
            if task_match:
                notif['task_id'] = task_match.group(1)

            message_match = re.search(r'Message: ([^\n]+)', match)
            if message_match:
                notif['message'] = message_match.group(1).strip()

            time_match = re.search(r'Time: ([^\n]+)', match)
            if time_match:
                notif['time'] = time_match.group(1).strip()

            link_match = re.search(r'Link: ([^\n]+)', match)
            if link_match:
                notif['link'] = link_match.group(1).strip()

            if notif:  # Only add if we parsed something
                notifications.append(notif)

        return notifications

    def mark_delivered(self, agent: str):
        """
        Move agent's pending notifications to delivered

        Call this after agent has read their notifications
        """
        if not os.path.exists(self.notifications_file):
            return

        with open(self.notifications_file, 'r') as f:
            content = f.read()

        # Extract pending section
        pending_match = re.search(
            r'(## Pending\n\n)(.*?)(## Delivered)',
            content,
            re.DOTALL
        )

        if not pending_match:
            return

        pending_header = pending_match.group(1)
        pending_content = pending_match.group(2)
        delivered_header = pending_match.group(3)

        # Find notifications for this agent
        pattern = rf'(### @{agent}\n.*?)(?=\n### @|\n## |\Z)'
        agent_notifs = re.findall(pattern, pending_content, re.DOTALL)

        if not agent_notifs:
            return

        # Remove from pending
        for notif in agent_notifs:
            pending_content = pending_content.replace(notif, '')

        # Add to delivered (with delivered timestamp)
        delivered_notifs = []
        for notif in agent_notifs:
            delivered_time = datetime.now().isoformat()[:16]
            notif_with_delivery = f"{notif}Delivered: {delivered_time}\n"
            delivered_notifs.append(notif_with_delivery)

        # Reconstruct file
        delivered_section_match = re.search(
            r'## Delivered\n\n(.*)',
            content,
            re.DOTALL
        )
        delivered_content = delivered_section_match.group(1) if delivered_section_match else ''

        new_content = (
            pending_header +
            pending_content +
            delivered_header + '\n\n' +
            ''.join(delivered_notifs) +
            delivered_content
        )

        with open(self.notifications_file, 'w') as f:
            f.write(new_content)

    def subscribe_to_task(self, agent: str, task_id: str):
        """
        Subscribe agent to task notifications

        Saves to agent's subscriptions.json
        """
        agent_dir = os.path.join(self.workspace, 'agents', agent)
        subscriptions_file = os.path.join(agent_dir, 'subscriptions.json')

        # Load existing subscriptions
        if os.path.exists(subscriptions_file):
            with open(subscriptions_file, 'r') as f:
                subscriptions = json.load(f)
        else:
            subscriptions = {}

        # Add subscription
        if task_id not in subscriptions:
            subscriptions[task_id] = {
                'subscribed_at': datetime.now().isoformat(),
                'reason': 'interaction'
            }

            # Save
            with open(subscriptions_file, 'w') as f:
                json.dump(subscriptions, f, indent=2)

    def is_subscribed(self, agent: str, task_id: str) -> bool:
        """Check if agent is subscribed to task"""
        agent_dir = os.path.join(self.workspace, 'agents', agent)
        subscriptions_file = os.path.join(agent_dir, 'subscriptions.json')

        if not os.path.exists(subscriptions_file):
            return False

        with open(subscriptions_file, 'r') as f:
            subscriptions = json.load(f)

        return task_id in subscriptions


# Convenience functions

_manager = None


def get_notification_manager(workspace_dir: str = 'workspace') -> NotificationManager:
    """Get singleton NotificationManager"""
    global _manager
    if _manager is None:
        _manager = NotificationManager(workspace_dir)
    return _manager


def notify(to_agent: str, from_agent: str, message: str, **kwargs):
    """Quick notification"""
    nm = get_notification_manager()
    nm.add_notification(to_agent, from_agent, message, **kwargs)


def check_notifications(agent: str) -> List[Dict[str, str]]:
    """Quick notification check"""
    nm = get_notification_manager()
    return nm.get_notifications(agent)


def mark_read(agent: str):
    """Quick mark as read"""
    nm = get_notification_manager()
    nm.mark_delivered(agent)
