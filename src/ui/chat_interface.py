"""
Chat Interface for SwarmBot UI
Provides a rich chat experience with message formatting, tool integration, and more
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
from typing import Dict, Any, Optional, List, Tuple, Callable
import asyncio
from datetime import datetime
import re
import json
from pathlib import Path
import logging
from .base import UIComponent

logger = logging.getLogger(__name__)


class ChatInterface(UIComponent):
    """Main chat interface component"""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, **kwargs)
        self.messages: List[Dict[str, Any]] = []
        self.current_input = ""
        self.history_index = -1
        self.input_history: List[str] = []
        self.is_processing = False
        self.auto_scroll = True
        
    def build(self) -> None:
        """Build the chat interface"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Create main container
        main_container = ttk.Frame(self.frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Chat display area
        self.create_chat_display(main_container)
        
        # Input area
        self.create_input_area(main_container)
        
        # Tool panel (collapsible)
        self.create_tool_panel(main_container)
        
        # Bind events
        self.bind_events()
        
    def create_chat_display(self, parent: tk.Widget) -> None:
        """Create the chat message display area"""
        # Frame for chat display
        chat_frame = ttk.Frame(parent)
        chat_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Text widget for messages
        self.chat_display = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=10,
            spacing1=2,
            spacing2=2,
            spacing3=2
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(chat_frame, command=self.chat_display.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_display.config(yscrollcommand=scrollbar.set)
        
        # Configure tags for different message types
        self.configure_text_tags()
        
        # Make read-only
        self.chat_display.config(state=tk.DISABLED)
        
        # Context menu
        self.create_context_menu()
        
    def configure_text_tags(self) -> None:
        """Configure text tags for formatting"""
        # Font configurations
        base_font = tkfont.Font(family="Segoe UI", size=11)
        bold_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        italic_font = tkfont.Font(family="Segoe UI", size=11, slant="italic")
        code_font = tkfont.Font(family="Consolas", size=10)
        
        # User message
        self.chat_display.tag_config(
            "user",
            font=base_font,
            foreground="#2196F3",
            spacing1=10,
            spacing3=5
        )
        
        # Assistant message
        self.chat_display.tag_config(
            "assistant",
            font=base_font,
            foreground="#4CAF50",
            spacing1=10,
            spacing3=5
        )
        
        # System message
        self.chat_display.tag_config(
            "system",
            font=italic_font,
            foreground="#FF9800",
            spacing1=5,
            spacing3=5
        )
        
        # Error message
        self.chat_display.tag_config(
            "error",
            font=base_font,
            foreground="#F44336",
            spacing1=5,
            spacing3=5
        )
        
        # Code block
        self.chat_display.tag_config(
            "code",
            font=code_font,
            background="#2D2D2D",
            foreground="#FFFFFF",
            relief=tk.SOLID,
            borderwidth=1,
            wrap=tk.NONE,
            lmargin1=20,
            lmargin2=20,
            rmargin=20,
            spacing1=5,
            spacing3=5
        )
        
        # Inline code
        self.chat_display.tag_config(
            "inline_code",
            font=code_font,
            background="#3D3D3D",
            foreground="#FFFFFF"
        )
        
        # Bold text
        self.chat_display.tag_config("bold", font=bold_font)
        
        # Italic text
        self.chat_display.tag_config("italic", font=italic_font)
        
        # Link
        self.chat_display.tag_config(
            "link",
            foreground="#2196F3",
            underline=True
        )
        
        # Timestamp
        self.chat_display.tag_config(
            "timestamp",
            font=tkfont.Font(family="Segoe UI", size=9),
            foreground="#757575"
        )
        
        # Tool execution
        self.chat_display.tag_config(
            "tool",
            font=italic_font,
            foreground="#9C27B0",
            background="#F3E5F5",
            relief=tk.FLAT,
            borderwidth=1,
            lmargin1=20,
            lmargin2=20,
            spacing1=5,
            spacing3=5
        )
        
        # Thinking/processing
        self.chat_display.tag_config(
            "thinking",
            font=italic_font,
            foreground="#607D8B"
        )
        
    def create_input_area(self, parent: tk.Widget) -> None:
        """Create the message input area"""
        # Input frame
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        
        # Input container with border
        input_container = ttk.Frame(input_frame, relief=tk.SOLID, borderwidth=1)
        input_container.grid(row=0, column=0, sticky="ew")
        input_container.columnconfigure(0, weight=1)
        
        # Multi-line input
        self.input_text = tk.Text(
            input_container,
            height=3,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=10
        )
        self.input_text.grid(row=0, column=0, sticky="ew")
        
        # Input scrollbar
        input_scrollbar = ttk.Scrollbar(
            input_container,
            command=self.input_text.yview
        )
        input_scrollbar.grid(row=0, column=1, sticky="ns")
        self.input_text.config(yscrollcommand=input_scrollbar.set)
        
        # Button frame
        button_frame = ttk.Frame(input_container)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        button_frame.columnconfigure(0, weight=1)
        
        # Mode indicator
        self.mode_label = ttk.Label(button_frame, text="Enhanced Mode")
        self.mode_label.grid(row=0, column=0, sticky="w")
        
        # Character count
        self.char_count_label = ttk.Label(button_frame, text="0 chars")
        self.char_count_label.grid(row=0, column=1, padx=10)
        
        # Send button
        self.send_button = ttk.Button(
            button_frame,
            text="Send",
            command=self.send_message,
            state=tk.NORMAL
        )
        self.send_button.grid(row=0, column=2, padx=(5, 0))
        
        # Stop button (hidden by default)
        self.stop_button = ttk.Button(
            button_frame,
            text="Stop",
            command=self.stop_generation,
            state=tk.DISABLED
        )
        # Don't grid yet
        
        # Typing indicator
        self.typing_label = ttk.Label(
            parent,
            text="",
            font=("Segoe UI", 9, "italic")
        )
        self.typing_label.grid(row=2, column=0, sticky="w", padx=5)
        
    def create_tool_panel(self, parent: tk.Widget) -> None:
        """Create collapsible tool panel"""
        # Tool frame
        self.tool_frame = ttk.LabelFrame(parent, text="Quick Tools", padding=5)
        # Initially hidden
        
        # Tool buttons grid
        tools = [
            ("📁", "Browse Files", "browse_files"),
            ("🔍", "Search Code", "search_code"),
            ("🌐", "Web Search", "web_search"),
            ("📝", "Create File", "create_file"),
            ("🛠️", "Execute Tool", "execute_tool"),
            ("📊", "Analyze Data", "analyze_data"),
        ]
        
        for i, (icon, tooltip, command) in enumerate(tools):
            btn = ttk.Button(
                self.tool_frame,
                text=icon,
                width=3,
                command=lambda cmd=command: self.quick_tool(cmd)
            )
            btn.grid(row=i // 3, column=i % 3, padx=2, pady=2)
            
            # Add tooltip
            self.create_tooltip(btn, tooltip)
            
    def create_context_menu(self) -> None:
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self.chat_display, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selection)
        self.context_menu.add_command(label="Copy All", command=self.copy_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Clear Chat", command=self.clear)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Save Chat", command=self.save_chat)
        self.context_menu.add_command(label="Load Chat", command=self.load_chat)
        
    def bind_events(self) -> None:
        """Bind keyboard and mouse events"""
        # Enter to send (with modifiers)
        self.input_text.bind("<Control-Return>", lambda e: self.send_message())
        self.input_text.bind("<Shift-Return>", lambda e: "break")  # New line
        
        # Input history navigation
        self.input_text.bind("<Up>", self.previous_input)
        self.input_text.bind("<Down>", self.next_input)
        
        # Character count update
        self.input_text.bind("<KeyRelease>", self.update_char_count)
        
        # Context menu
        self.chat_display.bind("<Button-3>", self.show_context_menu)
        
        # Link clicking
        self.chat_display.bind("<Button-1>", self.handle_click)
        
        # Auto-scroll toggle
        self.chat_display.bind("<MouseWheel>", self.on_mouse_wheel)
        
    def add_message(self, role: str, content: str, 
                   timestamp: Optional[datetime] = None,
                   tool_info: Optional[Dict[str, Any]] = None) -> None:
        """Add a message to the chat display"""
        if timestamp is None:
            timestamp = datetime.now()
            
        # Store message
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "tool_info": tool_info
        }
        self.messages.append(message)
        
        # Display message
        self.display_message(message)
        
        # Auto-scroll if enabled
        if self.auto_scroll:
            self.chat_display.see(tk.END)
            
    def display_message(self, message: Dict[str, Any]) -> None:
        """Display a message in the chat"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp if enabled
        if self.config.get("show_timestamps", True):
            timestamp_str = message["timestamp"].strftime("%H:%M:%S")
            self.chat_display.insert(tk.END, f"[{timestamp_str}] ", "timestamp")
            
        # Add role prefix
        role = message["role"]
        if role == "user":
            self.chat_display.insert(tk.END, "You: ", ("bold", "user"))
        elif role == "assistant":
            self.chat_display.insert(tk.END, "SwarmBot: ", ("bold", "assistant"))
        elif role == "system":
            self.chat_display.insert(tk.END, "System: ", ("bold", "system"))
        elif role == "error":
            self.chat_display.insert(tk.END, "Error: ", ("bold", "error"))
            
        # Add content with formatting
        self.insert_formatted_text(message["content"], role)
        
        # Add tool info if present
        if message.get("tool_info"):
            self.display_tool_info(message["tool_info"])
            
        # Add newline
        self.chat_display.insert(tk.END, "\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        
    def insert_formatted_text(self, text: str, base_tag: str) -> None:
        """Insert text with markdown-like formatting"""
        # Process markdown-like formatting
        # This is a simplified version - could be expanded
        
        # Code blocks
        code_pattern = r'```(\w*)\n(.*?)```'
        parts = re.split(code_pattern, text, flags=re.DOTALL)
        
        i = 0
        while i < len(parts):
            if i % 3 == 0:  # Regular text
                if parts[i]:
                    self.process_inline_formatting(parts[i], base_tag)
            elif i % 3 == 1:  # Language
                pass  # Skip language identifier
            else:  # Code content
                self.chat_display.insert(tk.END, parts[i], "code")
                
            i += 1
            
    def process_inline_formatting(self, text: str, base_tag: str) -> None:
        """Process inline formatting like bold, italic, code"""
        # Split by inline code first
        code_parts = re.split(r'`([^`]+)`', text)
        
        for i, part in enumerate(code_parts):
            if i % 2 == 0:  # Regular text
                # Process bold and italic
                formatted_parts = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', part)
                
                for fp in formatted_parts:
                    if fp.startswith("**") and fp.endswith("**"):
                        # Bold
                        self.chat_display.insert(tk.END, fp[2:-2], (base_tag, "bold"))
                    elif fp.startswith("*") and fp.endswith("*"):
                        # Italic
                        self.chat_display.insert(tk.END, fp[1:-1], (base_tag, "italic"))
                    else:
                        # Regular text
                        self.chat_display.insert(tk.END, fp, base_tag)
            else:  # Inline code
                self.chat_display.insert(tk.END, part, "inline_code")
                
    def display_tool_info(self, tool_info: Dict[str, Any]) -> None:
        """Display tool execution information"""
        self.chat_display.insert(tk.END, "\n", "")
        self.chat_display.insert(
            tk.END,
            f"🛠️ Tool: {tool_info['name']}\n",
            "tool"
        )
        
        if tool_info.get("parameters"):
            params_str = json.dumps(tool_info["parameters"], indent=2)
            self.chat_display.insert(tk.END, f"Parameters:\n{params_str}\n", "tool")
            
        if tool_info.get("result"):
            self.chat_display.insert(tk.END, f"Result: {tool_info['result']}\n", "tool")
            
    def send_message(self) -> None:
        """Send the current input message"""
        content = self.input_text.get("1.0", tk.END).strip()
        if not content or self.is_processing:
            return
            
        # Add to history
        self.input_history.append(content)
        self.history_index = len(self.input_history)
        
        # Clear input
        self.input_text.delete("1.0", tk.END)
        self.update_char_count()
        
        # Add user message
        self.add_message("user", content)
        
        # Show processing state
        self.set_processing(True)
        
        # Trigger send event
        self.trigger_event("send_message", content)
        
    def set_processing(self, processing: bool) -> None:
        """Set processing state"""
        self.is_processing = processing
        
        if processing:
            self.send_button.grid_remove()
            self.stop_button.grid(row=0, column=2, padx=(5, 0))
            self.stop_button.config(state=tk.NORMAL)
            self.input_text.config(state=tk.DISABLED)
            self.show_typing_indicator()
        else:
            self.stop_button.grid_remove()
            self.send_button.grid(row=0, column=2, padx=(5, 0))
            self.stop_button.config(state=tk.DISABLED)
            self.input_text.config(state=tk.NORMAL)
            self.hide_typing_indicator()
            self.input_text.focus()
            
    def show_typing_indicator(self) -> None:
        """Show typing indicator"""
        self.typing_animation_active = True
        self.animate_typing()
        
    def hide_typing_indicator(self) -> None:
        """Hide typing indicator"""
        self.typing_animation_active = False
        self.typing_label.config(text="")
        
    def animate_typing(self) -> None:
        """Animate typing indicator"""
        if not self.typing_animation_active:
            return
            
        # Cycle through dots
        current = self.typing_label.cget("text")
        if current == "":
            self.typing_label.config(text="SwarmBot is thinking.")
        elif current == "SwarmBot is thinking.":
            self.typing_label.config(text="SwarmBot is thinking..")
        elif current == "SwarmBot is thinking..":
            self.typing_label.config(text="SwarmBot is thinking...")
        else:
            self.typing_label.config(text="SwarmBot is thinking.")
            
        # Continue animation
        self.parent.after(500, self.animate_typing)
        
    def stop_generation(self) -> None:
        """Stop message generation"""
        self.trigger_event("stop_generation")
        self.set_processing(False)
        
    def previous_input(self, event) -> str:
        """Navigate to previous input in history"""
        if self.history_index > 0:
            # Save current input if at end of history
            if self.history_index == len(self.input_history):
                self.current_input = self.input_text.get("1.0", tk.END).strip()
                
            self.history_index -= 1
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", self.input_history[self.history_index])
            
        return "break"  # Prevent default behavior
        
    def next_input(self, event) -> str:
        """Navigate to next input in history"""
        if self.history_index < len(self.input_history):
            self.history_index += 1
            self.input_text.delete("1.0", tk.END)
            
            if self.history_index == len(self.input_history):
                # Restore saved current input
                self.input_text.insert("1.0", self.current_input)
            else:
                self.input_text.insert("1.0", self.input_history[self.history_index])
                
        return "break"
        
    def update_char_count(self, event=None) -> None:
        """Update character count label"""
        content = self.input_text.get("1.0", tk.END).strip()
        count = len(content)
        self.char_count_label.config(text=f"{count} chars")
        
        # Enable/disable send button
        self.send_button.config(state=tk.NORMAL if count > 0 else tk.DISABLED)
        
    def show_context_menu(self, event) -> None:
        """Show context menu"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
            
    def copy_selection(self) -> None:
        """Copy selected text"""
        try:
            selection = self.chat_display.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.parent.clipboard_clear()
            self.parent.clipboard_append(selection)
        except tk.TclError:
            pass  # No selection
            
    def copy_all(self) -> None:
        """Copy all chat content"""
        content = self.chat_display.get("1.0", tk.END).strip()
        self.parent.clipboard_clear()
        self.parent.clipboard_append(content)
        
    def clear(self) -> None:
        """Clear chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.messages.clear()
        
    def save_chat(self) -> None:
        """Save chat to file"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                if filename.endswith(".json"):
                    # Save as JSON
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.messages, f, indent=2, default=str)
                else:
                    # Save as plain text
                    content = self.chat_display.get("1.0", tk.END).strip()
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                self.add_message("system", f"Chat saved to {filename}")
            except Exception as e:
                self.add_message("error", f"Failed to save chat: {str(e)}")
                
    def load_chat(self) -> None:
        """Load chat from file"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                    
                self.clear()
                
                for msg in messages:
                    # Convert timestamp string back to datetime
                    if isinstance(msg.get("timestamp"), str):
                        msg["timestamp"] = datetime.fromisoformat(msg["timestamp"])
                    self.add_message(**msg)
                    
                self.add_message("system", f"Chat loaded from {filename}")
            except Exception as e:
                self.add_message("error", f"Failed to load chat: {str(e)}")
                
    def handle_click(self, event) -> None:
        """Handle clicks on links or special elements"""
        # Get clicked position
        index = self.chat_display.index(f"@{event.x},{event.y}")
        
        # Check if it's a link
        tags = self.chat_display.tag_names(index)
        if "link" in tags:
            # Get link URL (would need to be stored with tag)
            self.trigger_event("link_clicked", index)
            
    def on_mouse_wheel(self, event) -> None:
        """Handle mouse wheel scrolling"""
        # Disable auto-scroll if user scrolls up
        if event.delta > 0:  # Scrolling up
            view = self.chat_display.yview()
            if view[1] < 1.0:  # Not at bottom
                self.auto_scroll = False
        else:  # Scrolling down
            view = self.chat_display.yview()
            if view[1] >= 1.0:  # At bottom
                self.auto_scroll = True
                
    def quick_tool(self, tool_name: str) -> None:
        """Execute a quick tool"""
        self.trigger_event("quick_tool", tool_name)
        
    def create_tooltip(self, widget: tk.Widget, text: str) -> None:
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ttk.Label(
                tooltip,
                text=text,
                background="#ffffe0",
                relief=tk.SOLID,
                borderwidth=1
            )
            label.pack()
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, "tooltip"):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def toggle_tool_panel(self) -> None:
        """Toggle tool panel visibility"""
        if self.tool_frame.winfo_viewable():
            self.tool_frame.grid_remove()
        else:
            self.tool_frame.grid(row=3, column=0, sticky="ew", pady=5)
            
    def set_mode(self, mode: str) -> None:
        """Set chat mode indicator"""
        self.mode_label.config(text=f"{mode.title()} Mode")
        
    def append_to_last_message(self, content: str) -> None:
        """Append content to the last assistant message (for streaming)"""
        if self.messages and self.messages[-1]["role"] == "assistant":
            self.messages[-1]["content"] += content
            
            # Update display
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, content, "assistant")
            self.chat_display.config(state=tk.DISABLED)
            
            if self.auto_scroll:
                self.chat_display.see(tk.END)
