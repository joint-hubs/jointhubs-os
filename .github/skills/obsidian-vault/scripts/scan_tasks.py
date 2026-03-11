#!/usr/bin/env python3
"""
Obsidian Tasks Scanner

Scans all markdown files for Obsidian Tasks plugin syntax and extracts:
- Task text
- Status (done/not done)
- Due date (📅)
- Start date (🛫)
- Scheduled date (⏳)
- Priority (🔺 highest, ⏫ high, 🔼 medium, 🔽 low)
- Created date (➕)
- Done date (✅)

Usage:
    python scan_tasks.py [--json] [--pending] [--overdue]
"""

import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime, date
from dataclasses import dataclass, asdict
from typing import List, Optional


def find_second_brain() -> Path:
    """Find Second Brain directory by walking up from script location."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "Second Brain"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find 'Second Brain' directory")


@dataclass
class Task:
    text: str
    file_path: str
    line_number: int
    done: bool
    priority: Optional[str] = None  # highest, high, medium, low
    due_date: Optional[str] = None
    start_date: Optional[str] = None
    scheduled_date: Optional[str] = None
    created_date: Optional[str] = None
    done_date: Optional[str] = None
    
    @property
    def is_overdue(self) -> bool:
        if self.done or not self.due_date:
            return False
        try:
            due = datetime.strptime(self.due_date, '%Y-%m-%d').date()
            return due < date.today()
        except ValueError:
            return False
    
    @property
    def priority_order(self) -> int:
        """Lower is higher priority."""
        priority_map = {'highest': 0, 'high': 1, 'medium': 2, 'low': 3, None: 4}
        return priority_map.get(self.priority, 4)


# Emoji patterns for Obsidian Tasks
PATTERNS = {
    'due': r'📅\s*(\d{4}-\d{2}-\d{2})',
    'start': r'🛫\s*(\d{4}-\d{2}-\d{2})',
    'scheduled': r'⏳\s*(\d{4}-\d{2}-\d{2})',
    'created': r'➕\s*(\d{4}-\d{2}-\d{2})',
    'done_date': r'✅\s*(\d{4}-\d{2}-\d{2})',
}

PRIORITY_PATTERNS = {
    '🔺': 'highest',
    '⏫': 'high', 
    '🔼': 'medium',
    '🔽': 'low',
}


def parse_task_line(line: str, file_path: str, line_number: int) -> Optional[Task]:
    """Parse a single task line into a Task object."""
    
    # Match checkbox pattern: - [ ] or - [x]
    match = re.match(r'^[\s\-\*]*\[([ xX])\]\s*(.+)$', line)
    if not match:
        return None
    
    done = match.group(1).lower() == 'x'
    task_content = match.group(2)
    
    # Extract text (everything before the first emoji marker)
    text_match = re.match(r'^([^📅🛫⏳➕✅🔺⏫🔼🔽]+)', task_content)
    text = text_match.group(1).strip() if text_match else task_content.strip()
    
    # Extract dates
    due_date = None
    start_date = None
    scheduled_date = None
    created_date = None
    done_date = None
    
    for key, pattern in PATTERNS.items():
        m = re.search(pattern, task_content)
        if m:
            if key == 'due':
                due_date = m.group(1)
            elif key == 'start':
                start_date = m.group(1)
            elif key == 'scheduled':
                scheduled_date = m.group(1)
            elif key == 'created':
                created_date = m.group(1)
            elif key == 'done_date':
                done_date = m.group(1)
    
    # Extract priority
    priority = None
    for emoji, prio in PRIORITY_PATTERNS.items():
        if emoji in task_content:
            priority = prio
            break
    
    return Task(
        text=text,
        file_path=file_path,
        line_number=line_number,
        done=done,
        priority=priority,
        due_date=due_date,
        start_date=start_date,
        scheduled_date=scheduled_date,
        created_date=created_date,
        done_date=done_date,
    )


def scan_vault(vault_path: Path) -> List[Task]:
    """Scan all markdown files for tasks."""
    tasks = []
    
    for md_file in vault_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
            rel_path = str(md_file.relative_to(vault_path))
            
            for i, line in enumerate(content.split('\n'), 1):
                task = parse_task_line(line, rel_path, i)
                if task:
                    tasks.append(task)
                    
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    
    return tasks


def print_summary(tasks: List[Task], show_pending: bool = False, show_overdue: bool = False):
    """Print a human-readable summary."""
    
    if show_pending:
        tasks = [t for t in tasks if not t.done]
    if show_overdue:
        tasks = [t for t in tasks if t.is_overdue]
    
    # Sort by priority, then by due date
    tasks.sort(key=lambda t: (t.priority_order, t.due_date or '9999-99-99'))
    
    done_count = sum(1 for t in tasks if t.done)
    pending_count = len(tasks) - done_count
    overdue_count = sum(1 for t in tasks if t.is_overdue)
    
    print(f"\n{'='*60}")
    print(f"OBSIDIAN TASKS SCAN - Second Brain")
    print(f"{'='*60}\n")
    
    print(f"📋 Total tasks: {len(tasks)}")
    print(f"✅ Done: {done_count}")
    print(f"⏳ Pending: {pending_count}")
    print(f"🔴 Overdue: {overdue_count}\n")
    
    if show_overdue:
        print("🔴 OVERDUE TASKS:\n")
    elif show_pending:
        print("⏳ PENDING TASKS:\n")
    else:
        print("ALL TASKS:\n")
    
    # Group by priority
    by_priority = {'highest': [], 'high': [], 'medium': [], 'low': [], None: []}
    for task in tasks:
        by_priority[task.priority].append(task)
    
    priority_labels = {
        'highest': '🔺 Highest',
        'high': '⏫ High',
        'medium': '🔼 Medium',
        'low': '🔽 Low',
        None: '❓ No Priority'
    }
    
    for priority, label in priority_labels.items():
        priority_tasks = by_priority[priority]
        if priority_tasks:
            print(f"\n{label} ({len(priority_tasks)})")
            print("-" * 40)
            for task in priority_tasks:
                status = "✅" if task.done else "⏳"
                overdue = " 🔴 OVERDUE" if task.is_overdue else ""
                due_str = f" (due: {task.due_date})" if task.due_date else ""
                print(f"  {status} {task.text}{due_str}{overdue}")
                print(f"     📄 {task.file_path}:{task.line_number}")
    
    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Scan Obsidian vault for tasks')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--pending', action='store_true', help='Show only pending tasks')
    parser.add_argument('--overdue', action='store_true', help='Show only overdue tasks')
    parser.add_argument('--path', type=str, help='Custom vault path')
    args = parser.parse_args()
    
    try:
        vault_path = Path(args.path) if args.path else find_second_brain()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    if not vault_path.exists():
        print(f"Error: Vault path not found: {vault_path}")
        return 1
    
    tasks = scan_vault(vault_path)
    
    if args.json:
        # Filter if needed
        if args.pending:
            tasks = [t for t in tasks if not t.done]
        if args.overdue:
            tasks = [t for t in tasks if t.is_overdue]
        
        json_output = {
            'total': len(tasks),
            'done': sum(1 for t in tasks if t.done),
            'pending': sum(1 for t in tasks if not t.done),
            'overdue': sum(1 for t in tasks if t.is_overdue),
            'tasks': [asdict(t) for t in tasks]
        }
        print(json.dumps(json_output, indent=2, default=str))
    else:
        print_summary(tasks, show_pending=args.pending, show_overdue=args.overdue)
    
    return 0


if __name__ == '__main__':
    exit(main())
