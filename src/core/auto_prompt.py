#!/usr/bin/env python3
"""
SwarmBot Auto-Prompt System
Enables the bot to automatically continue tasks until completion
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class AutoPromptSystem:
    """Manages automatic task continuation for SwarmBot"""
    
    def __init__(self, project_root: Path = None):
        """Initialize the auto-prompt system"""
        self.project_root = project_root or Path.cwd()
        self.task_queue = []
        self.completed_tasks = []
        self.current_task = None
        self.max_iterations = 10  # Safety limit
        self.iteration_count = 0
        
    def add_task(self, task: Dict[str, Any]) -> None:
        """Add a task to the queue"""
        task['id'] = f"task_{datetime.now().timestamp()}"
        task['status'] = 'pending'
        task['created_at'] = datetime.now().isoformat()
        self.task_queue.append(task)
        
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the next pending task"""
        for task in self.task_queue:
            if task['status'] == 'pending':
                return task
        return None
        
    def mark_task_complete(self, task_id: str, result: Any = None) -> None:
        """Mark a task as complete"""
        for task in self.task_queue:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                task['result'] = result
                self.completed_tasks.append(task)
                break
                
    def should_continue(self) -> bool:
        """Check if auto-prompting should continue"""
        if self.iteration_count >= self.max_iterations:
            print(f"[AUTO-PROMPT] Reached maximum iterations ({self.max_iterations})")
            return False
            
        pending_tasks = [t for t in self.task_queue if t['status'] == 'pending']
        return len(pending_tasks) > 0
        
    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """Execute a single task"""
        print(f"\n[AUTO-PROMPT] Executing task: {task.get('description', 'Unknown')}")
        
        # Here you would integrate with the actual SwarmBot functionality
        # For now, this is a placeholder
        task_type = task.get('type', 'generic')
        
        if task_type == 'file_operation':
            return await self.handle_file_operation(task)
        elif task_type == 'code_generation':
            return await self.handle_code_generation(task)
        elif task_type == 'validation':
            return await self.handle_validation(task)
        else:
            return await self.handle_generic_task(task)
            
    async def handle_file_operation(self, task: Dict[str, Any]) -> Any:
        """Handle file operations - always save to project directory unless specified"""
        file_path = task.get('file_path')
        
        # If no absolute path specified, use project directory
        if file_path and not Path(file_path).is_absolute():
            file_path = self.project_root / file_path
            task['file_path'] = str(file_path)
            
        # Execute the file operation
        operation = task.get('operation', 'write')
        content = task.get('content', '')
        
        try:
            if operation == 'write':
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')
                return f"File written: {file_path}"
            elif operation == 'read':
                return file_path.read_text(encoding='utf-8')
            else:
                return f"Unknown operation: {operation}"
        except Exception as e:
            return f"Error: {e}"
            
    async def handle_code_generation(self, task: Dict[str, Any]) -> Any:
        """Handle code generation tasks"""
        # Placeholder for code generation
        return "Code generation completed"
        
    async def handle_validation(self, task: Dict[str, Any]) -> Any:
        """Handle validation tasks"""
        # Placeholder for validation
        return "Validation completed"
        
    async def handle_generic_task(self, task: Dict[str, Any]) -> Any:
        """Handle generic tasks"""
        # Placeholder for generic tasks
        await asyncio.sleep(1)  # Simulate work
        return "Task completed"
        
    async def run(self) -> None:
        """Run the auto-prompt system"""
        print("[AUTO-PROMPT] Starting automatic task execution")
        print(f"[AUTO-PROMPT] Tasks in queue: {len(self.task_queue)}")
        
        while self.should_continue():
            self.iteration_count += 1
            
            # Get next task
            task = self.get_next_task()
            if not task:
                break
                
            self.current_task = task
            print(f"\n[AUTO-PROMPT] Iteration {self.iteration_count}/{self.max_iterations}")
            print(f"[AUTO-PROMPT] Current task: {task.get('description', 'Unknown')}")
            
            # Execute task
            try:
                result = await self.execute_task(task)
                self.mark_task_complete(task['id'], result)
                print(f"[AUTO-PROMPT] Task completed: {result}")
            except Exception as e:
                print(f"[AUTO-PROMPT] Task failed: {e}")
                task['status'] = 'failed'
                task['error'] = str(e)
                
            # Small delay between tasks
            await asyncio.sleep(0.5)
            
        # Summary
        print("\n[AUTO-PROMPT] Execution complete")
        print(f"[AUTO-PROMPT] Total iterations: {self.iteration_count}")
        print(f"[AUTO-PROMPT] Completed tasks: {len(self.completed_tasks)}")
        print(f"[AUTO-PROMPT] Remaining tasks: {len([t for t in self.task_queue if t['status'] == 'pending'])}")
        
    def save_state(self, file_path: Optional[Path] = None) -> None:
        """Save the current state to a file"""
        if not file_path:
            file_path = self.project_root / '.swarmbot_auto_state.json'
            
        state = {
            'task_queue': self.task_queue,
            'completed_tasks': self.completed_tasks,
            'iteration_count': self.iteration_count,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
            
    def load_state(self, file_path: Optional[Path] = None) -> None:
        """Load state from a file"""
        if not file_path:
            file_path = self.project_root / '.swarmbot_auto_state.json'
            
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
                
            self.task_queue = state.get('task_queue', [])
            self.completed_tasks = state.get('completed_tasks', [])
            self.iteration_count = state.get('iteration_count', 0)


# Integration with SwarmBot
def create_auto_prompt_tasks(user_request: str) -> List[Dict[str, Any]]:
    """Create tasks from a user request"""
    # This would be enhanced with NLP to parse the request
    # For now, just a simple example
    tasks = []
    
    if "fix" in user_request.lower() and "unicode" in user_request.lower():
        tasks.append({
            'type': 'validation',
            'description': 'Scan for Unicode/emoji characters',
            'action': 'scan_unicode'
        })
        tasks.append({
            'type': 'file_operation',
            'description': 'Fix Unicode issues in all files',
            'action': 'fix_unicode'
        })
        
    if "test" in user_request.lower():
        tasks.append({
            'type': 'validation',
            'description': 'Run all tests',
            'action': 'run_tests'
        })
        
    if "validate" in user_request.lower():
        tasks.append({
            'type': 'validation',
            'description': 'Validate configuration',
            'action': 'validate_config'
        })
        
    return tasks


if __name__ == "__main__":
    # Example usage
    async def main():
        auto_prompt = AutoPromptSystem()
        
        # Add some example tasks
        auto_prompt.add_task({
            'type': 'validation',
            'description': 'Check project structure'
        })
        auto_prompt.add_task({
            'type': 'file_operation',
            'description': 'Create test file',
            'operation': 'write',
            'file_path': 'test_output.txt',
            'content': 'This is a test file created by auto-prompt'
        })
        
        # Run the system
        await auto_prompt.run()
        
        # Save state
        auto_prompt.save_state()
        
    asyncio.run(main())
