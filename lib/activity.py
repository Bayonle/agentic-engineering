"""
Activity Logging System

Provides a unified activity feed showing all agent actions.
Simple append-only log with search/filter utilities.
"""

import os
from datetime import datetime
from typing import List, Optional


class ActivityLogger:
    """Manages the global activity feed"""

    def __init__(self, workspace_dir: str = 'workspace'):
        self.activity_log = os.path.join(workspace_dir, 'activity.log')

    def log(self, agent: str, message: str):
        """
        Log an activity

        Args:
            agent: Agent name (pm, engineer, qa, etc)
            message: Activity description

        Example:
            activity.log('engineer', 'Completed auth API implementation')
        """
        timestamp = datetime.now().isoformat()
        log_line = f"{timestamp} | {agent} | {message}\n"

        with open(self.activity_log, 'a') as f:
            f.write(log_line)

    def recent(self, n: int = 50) -> List[str]:
        """Get n most recent activities"""
        if not os.path.exists(self.activity_log):
            return []

        with open(self.activity_log, 'r') as f:
            lines = f.readlines()

        return lines[-n:]

    def today(self) -> List[str]:
        """Get today's activities"""
        today_str = datetime.now().strftime('%Y-%m-%d')

        if not os.path.exists(self.activity_log):
            return []

        with open(self.activity_log, 'r') as f:
            lines = f.readlines()

        return [line for line in lines if line.startswith(today_str)]

    def by_agent(self, agent: str, n: int = 50) -> List[str]:
        """Get recent activities by specific agent"""
        if not os.path.exists(self.activity_log):
            return []

        with open(self.activity_log, 'r') as f:
            lines = f.readlines()

        agent_lines = [line for line in lines if f' | {agent} | ' in line]
        return agent_lines[-n:]

    def search(self, query: str) -> List[str]:
        """Search activities for query string"""
        if not os.path.exists(self.activity_log):
            return []

        with open(self.activity_log, 'r') as f:
            lines = f.readlines()

        return [line for line in lines if query.lower() in line.lower()]


# Convenience functions

_logger = None


def get_logger(workspace_dir: str = 'workspace') -> ActivityLogger:
    """Get singleton ActivityLogger"""
    global _logger
    if _logger is None:
        _logger = ActivityLogger(workspace_dir)
    return _logger


def log_activity(agent: str, message: str):
    """Quick activity logging"""
    logger = get_logger()
    logger.log(agent, message)


def recent_activity(n: int = 50) -> List[str]:
    """Quick access to recent activity"""
    logger = get_logger()
    return logger.recent(n)


def today_activity() -> List[str]:
    """Quick access to today's activity"""
    logger = get_logger()
    return logger.today()
