"""
Enhanced Chat Session module for SwarmBot
Includes automatic tool selection and execution capabilities
"""

import json
import logging
from typing import List, Dict, Any, Tuple
import asyncio

from .chat_session import ChatSession
from .server import Server
from .tool import Tool
from .llm_client import LLMClient
from .tool_matcher import ToolMatcher, ToolMatch
from .core.auto_prompt import AutoPromptSystem

logger = logging.getLogger(__name__)


class EnhancedChatSession(ChatSession):
    """Enhanced chat session with automatic tool selection and execution."""
    
    def __init__(self, servers: List[Server], llm_client: LLMClient):
        super().__init__(servers, llm_client)
        self.tool_matcher = ToolMatcher()
        self.auto_mode = True  # Enable automatic tool execution by default
        self.tool_chain_limit = 5  # Maximum tools to chain in one request
        
        # Initialize auto-prompt system based on configuration
        self.auto_prompt_system = None
        self.auto_prompt_enabled = False
        self.auto_prompt_iterations = 0
        self.max_auto_prompt_iterations = 1
        self.auto_prompt_goal_detection = True
        self.auto_prompt_save_state = True
        
        # Check if any server has auto-prompt configuration
        if servers and hasattr(servers[0], 'config'):
            config = servers[0].config
            if hasattr(config, 'auto_prompt_enabled'):
                self.auto_prompt_enabled = config.auto_prompt_enabled
                self.max_auto_prompt_iterations = config.auto_prompt_max_iterations
                self.auto_prompt_goal_detection = config.auto_prompt_goal_detection
                self.auto_prompt_save_state = config.auto_prompt_save_state
                
                if self.auto_prompt_enabled:
                    self.auto_prompt_system = AutoPromptSystem()
                    logger.info(f"Auto-prompt system initialized (max iterations: {self.max_auto_prompt_iterations})")
    
    def build_enhanced_system_prompt(self) -> str:
        """Build an enhanced system prompt that encourages automatic tool use."""
        tools_by_category = self._categorize_tools()
        
        prompt = f"""You are SwarmBot, an advanced AI assistant with automatic tool selection and execution capabilities.

You have access to {len(self.all_tools)} tools across {len(self.active_servers)} active servers.

AUTOMATIC TOOL EXECUTION MODE: ENABLED
When the user asks for something that requires tool use, you should:
1. Automatically identify the appropriate tool(s)
2. Execute them without asking for permission
3. Chain multiple tools if needed to complete the task
4. Provide a natural response with the results

TOOL CATEGORIES AND CAPABILITIES:
"""
        
        for category, tools in tools_by_category.items():
            prompt += f"\n{category}:\n"
            for tool in tools[:5]:  # Show top 5 tools per category
                prompt += f"  - {tool.name}: {tool.description}\n"
            if len(tools) > 5:
                prompt += f"  ... and {len(tools) - 5} more\n"
        
        prompt += """
INTELLIGENT BEHAVIOR:
- Automatically use tools when the user's request implies it
- Chain multiple tools to complete complex tasks
- Don't ask for permission unless the operation is destructive
- Provide helpful context and explanations with results
- If multiple tools could work, choose the most appropriate one

TOOL RESPONSE FORMAT:
When you need to use a tool, respond with ONLY this JSON:
{
    "tool": "exact-tool-name",
    "arguments": {
        "param": "value"
    },
    "reasoning": "Brief explanation of why this tool"
}

For tool chains, use:
{
    "tool_chain": [
        {"tool": "tool1", "arguments": {...}},
        {"tool": "tool2", "arguments": {...}}
    ],
    "reasoning": "Explanation of the workflow"
}

Remember: Be proactive, intelligent, and helpful!"""
        
        return prompt
    
    def _categorize_tools(self) -> Dict[str, List[Tool]]:
        """Categorize tools by their function."""
        categories = {
            'File Operations': [],
            'Git & Version Control': [],
            'Task Management': [],
            'Search & Discovery': [],
            'Development Tools': [],
            'AI & Analysis': [],
            'Communication': [],
            'Other': []
        }
        
        for tool in self.all_tools:
            name_lower = tool.name.lower()
            
            if any(word in name_lower for word in ['file', 'read', 'write', 'directory']):
                categories['File Operations'].append(tool)
            elif 'git' in name_lower:
                categories['Git & Version Control'].append(tool)
            elif any(word in name_lower for word in ['task', 'todo', 'project']):
                categories['Task Management'].append(tool)
            elif 'search' in name_lower or 'find' in name_lower:
                categories['Search & Discovery'].append(tool)
            elif any(word in name_lower for word in ['code', 'debug', 'test']):
                categories['Development Tools'].append(tool)
            elif any(word in name_lower for word in ['reason', 'think', 'analyze']):
                categories['AI & Analysis'].append(tool)
            elif any(word in name_lower for word in ['email', 'message', 'slack']):
                categories['Communication'].append(tool)
            else:
                categories['Other'].append(tool)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    async def process_with_auto_tools(self, user_input: str) -> str:
        """Process user input with automatic tool selection."""
        # Find matching tools
        matches = self.tool_matcher.find_matching_tools(user_input, self.all_tools)
        
        if not matches:
            return None  # Let LLM handle it normally
        
        # If high confidence match, execute automatically
        if matches[0].confidence > 0.6:
            logger.info(f"Auto-executing tool: {matches[0].tool_name} (confidence: {matches[0].confidence:.2f})")
            
            # Build tool call
            tool_call = {
                "tool": matches[0].tool_name,
                "arguments": matches[0].suggested_args,
                "reasoning": f"Automatically selected based on: {matches[0].reasoning}"
            }
            
            return json.dumps(tool_call)
        
        # If medium confidence, suggest to LLM
        elif matches[0].confidence > 0.4:
            # Add context to help LLM decide
            context = f"Potential tools: {', '.join([m.tool_name for m in matches[:3]])}"
            self.conversation_history.append({
                "role": "system",
                "content": f"Tool suggestion: {context}"
            })
        
        return None
    
    async def execute_tool_chain(self, tool_chain: List[Dict]) -> List[Tuple[str, Any]]:
        """Execute a chain of tools in sequence."""
        results = []
        
        for i, tool_spec in enumerate(tool_chain[:self.tool_chain_limit]):
            tool_name = tool_spec['tool']
            arguments = tool_spec.get('arguments', {})
            
            logger.info(f"Executing tool {i+1}/{len(tool_chain)}: {tool_name}")
            
            # Find server with tool
            executed = False
            for server in self.active_servers:
                tools = await server.list_tools()
                if any(tool.name == tool_name for tool in tools):
                    success, result = await server.execute_tool(tool_name, arguments)
                    results.append((tool_name, result))
                    executed = True
                    
                    # Use result for next tool if needed
                    if success and i < len(tool_chain) - 1:
                        # Pass results to next tool if it needs them
                        next_tool = tool_chain[i + 1]
                        if 'use_previous_result' in next_tool.get('arguments', {}):
                            next_tool['arguments']['data'] = result
                    break
            
            if not executed:
                results.append((tool_name, f"Tool not found: {tool_name}"))
        
        return results
    
    async def enhanced_process_response(self, llm_response: str, user_input: str) -> str:
        """Enhanced response processing with auto-tool support."""
        try:
            response_data = json.loads(llm_response)
            
            # Handle tool chains
            if "tool_chain" in response_data:
                logger.info("Executing tool chain...")
                results = await self.execute_tool_chain(response_data["tool_chain"])
                
                formatted_results = []
                for tool_name, result in results:
                    formatted = self.format_tool_result(tool_name, result)
                    formatted_results.append(f"[{tool_name}]\n{formatted}")
                
                return "🔗 Tool Chain Results:\n\n" + "\n\n".join(formatted_results)
            
            # Handle single tool
            elif "tool" in response_data and "arguments" in response_data:
                tool_name = response_data["tool"]
                arguments = response_data["arguments"]
                reasoning = response_data.get("reasoning", "")
                
                if reasoning:
                    logger.info(f"Tool reasoning: {reasoning}")
                
                # Execute tool
                for server in self.active_servers:
                    tools = await server.list_tools()
                    if any(tool.name == tool_name for tool in tools):
                        success, result = await server.execute_tool(tool_name, arguments)
                        
                        if success:
                            formatted = self.format_tool_result(tool_name, result)
                            return f"✅ {reasoning}\n\n{formatted}"
                        else:
                            return f"❌ Tool execution failed: {result}"
                
                return f"⚠️ Tool '{tool_name}' not found"
            
            return llm_response
            
        except json.JSONDecodeError:
            return llm_response
    
    def format_tool_result(self, tool_name: str, result: Any) -> str:
        """Format tool results for better readability."""
        if isinstance(result, dict):
            if 'error' in result:
                return f"❌ Error: {result['error']}"
            
            # Special formatting for common tools
            if tool_name == 'get_tasks':
                return self._format_task_list(result)
            elif tool_name == 'read_file':
                return self._format_file_content(result)
            elif tool_name == 'list_directory':
                return self._format_directory_listing(result)
            else:
                return json.dumps(result, indent=2)
        
        elif isinstance(result, list):
            return self._format_list_result(result)
        else:
            return str(result)
    
    def _format_task_list(self, tasks: Any) -> str:
        """Format task list for display."""
        if isinstance(tasks, dict) and 'tasks' in tasks:
            tasks = tasks['tasks']
        
        if not tasks:
            return "📋 No tasks found"
        
        output = "📋 Tasks:\n"
        for task in tasks:
            status_emoji = {
                'pending': '⏳',
                'in-progress': '🔄',
                'done': '✅',
                'cancelled': '❌'
            }.get(task.get('status', 'pending'), '❓')
            
            output += f"\n{status_emoji} [{task.get('id', '?')}] {task.get('title', 'Untitled')}"
            if task.get('description'):
                output += f"\n    {task['description'][:100]}..."
        
        return output
    def _format_file_content(self, content: Any) -> str:
        """Format file content for display."""
        if isinstance(content, dict):
            content = content.get('content', str(content))
        
        lines = str(content).split('\n')
        if len(lines) > 50:
            return f"📄 File Content (showing first 25 and last 25 lines):\n\n" + \
                   '\n'.join(lines[:25]) + \
                   f"\n\n... ({len(lines) - 50} lines omitted) ...\n\n" + \
                   '\n'.join(lines[-25:])
        else:
            return f"📄 File Content:\n\n{content}"
    
    def _format_directory_listing(self, listing: Any) -> str:
        """Format directory listing."""
        if isinstance(listing, str):
            return f"📁 Directory Contents:\n{listing}"
        
        output = "📁 Directory Contents:\n"
        for item in listing:
            if isinstance(item, dict):
                name = item.get('name', 'Unknown')
                type_emoji = '📁' if item.get('type') == 'directory' else '📄'
                output += f"\n{type_emoji} {name}"
            else:
                output += f"\n📄 {item}"
        
        return output
    
    def _format_list_result(self, items: List) -> str:
        """Format list results."""
        if not items:
            return "No results found"
        
        output = f"Found {len(items)} items:\n"
        for i, item in enumerate(items[:10], 1):
            output += f"\n{i}. {item}"
        
        if len(items) > 10:
            output += f"\n\n... and {len(items) - 10} more"
        
        return output
    
    async def start_enhanced(self) -> None:
        """Enhanced chat session with auto-tool support."""
        print("\n🚀 SwarmBot Enhanced - Automatic Tool Mode")
        print("=" * 60)
        
        try:
            # Initialize servers
            await self.initialize_servers()
            
            if not self.active_servers:
                print("\n❌ No servers could be initialized. Exiting.")
                return
            
            # Load tools
            await self.load_tools()
            
            print(f"\n✅ Initialized with {len(self.active_servers)} servers and {len(self.all_tools)} tools")
            print(f"🤖 Automatic tool execution: {'ENABLED' if self.auto_mode else 'DISABLED'}")
            if self.auto_prompt_enabled:
                print(f"🔄 Auto-prompt: ENABLED (max {self.max_auto_prompt_iterations} iterations)")
            print("\n💡 Tips:")
            print("  - Just describe what you want, and I'll use the right tools")
            print("  - Type 'manual' to toggle automatic mode")
            print("  - Type 'help' for more commands")
            print("=" * 60)
            
            # Build enhanced system prompt
            system_message = {
                "role": "system",
                "content": self.build_enhanced_system_prompt()
            }
            self.conversation_history = [system_message]
            
            while True:
                try:
                    user_input = input("\n🧑 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle special commands
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("\n👋 Goodbye!")
                        break
                    
                    if user_input.lower() == 'help':
                        self.show_enhanced_help()
                        continue
                    
                    if user_input.lower() == 'manual':
                        self.auto_mode = not self.auto_mode
                        print(f"\n🔄 Automatic mode: {'ENABLED' if self.auto_mode else 'DISABLED'}")
                        continue
                    
                    if user_input.lower() == 'tools':
                        self.show_categorized_tools()
                        continue
                    
                    # Reset auto-prompt counter for new user input
                    self.auto_prompt_iterations = 0
                    
                    # Add user message
                    self.conversation_history.append({"role": "user", "content": user_input})
                    
                    # Try automatic tool matching first (if enabled)
                    auto_response = None
                    if self.auto_mode:
                        auto_response = await self.process_with_auto_tools(user_input)
                    
                    # Get LLM response
                    print("\n🤖 SwarmBot: ", end="", flush=True)
                    
                    if auto_response:
                        # Use auto-generated tool call
                        llm_response = auto_response
                        print("[Auto-tool mode] ", end="", flush=True)
                    else:
                        # Get LLM response
                        llm_response = self.llm_client.get_response(self.conversation_history)
                    
                    # Process response
                    result = await self.enhanced_process_response(llm_response, user_input)
                    
                    if result != llm_response:
                        # Tool was executed
                        print(result)
                        
                        # Update conversation
                        self.conversation_history.append({"role": "assistant", "content": llm_response})
                        self.conversation_history.append({"role": "system", "content": f"Tool result: {result}"})
                        
                        # Get natural language summary
                        summary_prompt = [{
                            "role": "system",
                            "content": "Provide a brief, natural summary of the tool execution results. Be conversational and helpful."
                        }, {
                            "role": "user",
                            "content": f"Tool executed: {llm_response}\nResult: {result}\nSummarize this naturally."
                        }]
                        
                        summary = self.llm_client.get_response(summary_prompt)
                        print(f"\n💬 {summary}")
                        self.conversation_history.append({"role": "assistant", "content": summary})
                        
                        # Check for auto-prompt after tool execution
                        if await self.handle_auto_prompt(summary):
                            # Auto-prompt triggered - continue the loop
                            continue
                    else:
                        # Regular response
                        print(llm_response)
                        self.conversation_history.append({"role": "assistant", "content": llm_response})
                        
                        # Check for auto-prompt
                        if await self.handle_auto_prompt(llm_response):
                            # Auto-prompt triggered - continue the loop with the new prompt
                            continue
                
                except KeyboardInterrupt:
                    print("\n\n⚠️  Interrupted. Type 'quit' to exit properly.")
                except Exception as e:
                    logger.error(f"Error in chat loop: {e}")
                    print(f"\n❌ Error: {str(e)}")
        
        finally:
            await self.cleanup_servers()
    
    def detect_incomplete_goal(self, response: str) -> bool:
        """Detect if the response indicates an incomplete goal or task."""
        if not self.auto_prompt_goal_detection:
            return False
        
        # Normalize response for checking
        response_lower = response.lower()
        
        # Indicators that suggest more work is needed
        continuation_indicators = [
            # Direct indicators
            "next step", "then we need to", "after that", "following this",
            "additionally", "furthermore", "let me continue", "continuing with",
            
            # Task progression indicators  
            "step 1", "step 2", "first,", "second,", "third,", "finally,",
            "to begin", "to start", "starting with", "beginning with",
            
            # Incomplete action indicators
            "i'll need to", "i need to", "we should", "we need to",
            "let's proceed", "now let's", "now we can", "next, we",
            
            # Planning indicators
            "here's the plan", "here's what we'll do", "the process will be",
            "this involves", "we'll start by", "the approach is",
            
            # Continuation questions
            "shall i continue?", "should i proceed?", "would you like me to continue?",
            "ready to proceed?", "shall we move forward?"
        ]
        
        # Check for explicit completion indicators (negative signals)
        completion_indicators = [
            "task completed", "all done", "finished", "that's everything",
            "process complete", "successfully completed", "work is done",
            "nothing more to do", "that covers everything", "all set"
        ]
        
        # Strong completion signals override continuation
        for indicator in completion_indicators:
            if indicator in response_lower:
                return False
        
        # Check for continuation indicators
        for indicator in continuation_indicators:
            if indicator in response_lower:
                logger.info(f"Auto-prompt: Detected incomplete goal - found '{indicator}'")
                return True
        
        # Check for numbered lists that might indicate multi-step processes
        import re
        numbered_steps = re.findall(r'\b\d+\.\s+\w+', response)
        if len(numbered_steps) >= 3:
            logger.info("Auto-prompt: Detected multi-step process")
            return True
        
        # Check if response ends with ellipsis or similar
        if response.rstrip().endswith(('...', '…', 'etc.', 'and so on')):
            logger.info("Auto-prompt: Detected trailing ellipsis")
            return True
        
        return False
    
    async def generate_continuation_prompt(self, context: List[Dict[str, str]]) -> str:
        """Generate an appropriate continuation prompt based on context."""
        # Get the last assistant response
        last_response = ""
        for msg in reversed(context):
            if msg["role"] == "assistant":
                last_response = msg["content"]
                break
        
        # Analyze what kind of continuation is needed
        if "step" in last_response.lower() or "next" in last_response.lower():
            return "Please continue with the next step."
        elif "?" in last_response[-50:]:  # Question near the end
            return "Yes, please proceed."
        elif any(word in last_response.lower() for word in ["plan", "approach", "process"]):
            return "Please execute this plan."
        else:
            return "Please continue with the task."
    
    async def handle_auto_prompt(self, llm_response: str) -> bool:
        """Handle auto-prompt logic. Returns True if auto-prompt was triggered."""
        if not self.auto_prompt_enabled or not self.auto_prompt_system:
            return False
        
        # Check if we've reached the iteration limit
        if self.auto_prompt_iterations >= self.max_auto_prompt_iterations:
            logger.info(f"Auto-prompt: Reached maximum iterations ({self.max_auto_prompt_iterations})")
            return False
        
        # Detect if goal is incomplete
        if not self.detect_incomplete_goal(llm_response):
            return False
        
        # Increment iteration counter
        self.auto_prompt_iterations += 1
        
        # Generate continuation prompt
        continuation_prompt = await self.generate_continuation_prompt(self.conversation_history)
        
        # Show auto-prompt indicator
        print(f"\n🔄 [AUTO-PROMPT {self.auto_prompt_iterations}/{self.max_auto_prompt_iterations}] {continuation_prompt}")
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": continuation_prompt})
        
        # Save state if enabled
        if self.auto_prompt_save_state and self.auto_prompt_system:
            self.auto_prompt_system.add_task({
                'type': 'continuation',
                'description': continuation_prompt,
                'iteration': self.auto_prompt_iterations,
                'context': llm_response[:500]  # Save partial context
            })
            self.auto_prompt_system.save_state()
        
        return True
    
    def show_enhanced_help(self) -> None:
        """Show enhanced help information."""
        print("\n📚 SwarmBot Enhanced - Commands:")
        print("  help     - Show this help message")
        print("  tools    - List tools by category")
        print("  manual   - Toggle automatic tool mode")
        print("  quit     - Exit the application")
        
        if self.auto_prompt_enabled:
            print(f"\n🔄 Auto-Prompt Status:")
            print(f"  Enabled: Yes")
            print(f"  Max iterations: {self.max_auto_prompt_iterations}")
            print(f"  Goal detection: {'Yes' if self.auto_prompt_goal_detection else 'No'}")
            print(f"  State saving: {'Yes' if self.auto_prompt_save_state else 'No'}")
        
        print("\n🎯 Automatic Tool Examples:")
        print("  'Show me all tasks' → Automatically runs get_tasks")
        print("  'Read config.json' → Automatically runs read_file")
        print("  'Search for TODO comments' → Automatically runs search_code")
        print("  'What changed in git?' → Automatically runs git_status")
        print("\n💡 Just describe what you want naturally!")
    
    def show_categorized_tools(self) -> None:
        """Show tools organized by category."""
        categories = self._categorize_tools()
        
        print(f"\n🔧 Available Tools by Category ({len(self.all_tools)} total):")
        
        for category, tools in categories.items():
            print(f"\n📂 {category} ({len(tools)} tools):")
            for tool in tools:
                # Show simplified description
                desc = tool.description[:60] + "..." if len(tool.description) > 60 else tool.description
                print(f"  • {tool.name}: {desc}")