#!/usr/bin/env python3
"""
Multi-Language Script Editor with MCP Tool Integration
A cross-platform script editor that supports multiple programming languages
and provides interfaces for MCP (Model Context Protocol) tool integration.

Features:
- Multi-language support (Python, PowerShell, Bash, CMD, etc.)
- Syntax highlighting
- Script execution with output capture
- MCP tool input/output interfaces
- File operations (New, Open, Save, Save As)
- Error handling and debugging
- Cross-platform compatibility

Based on research from:
- tkform (boscoh/tkform): GUI framework for script execution
- Real Python Tkinter tutorials: GUI development patterns
- Multi-language IDE projects: Language support strategies
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
import json
import tempfile
from pathlib import Path
import re
from typing import Dict, List, Optional, Callable


class LanguageConfig:
    """Configuration for supported programming languages"""
    
    LANGUAGES = {
        'python': {
            'name': 'Python',
            'extensions': ['.py', '.pyw'],
            'interpreter': [sys.executable],
            'comment': '#',
            'keywords': ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except'],
            'syntax_colors': {
                'keywords': '#0000FF',
                'strings': '#008000',
                'comments': '#808080',
                'numbers': '#FF4500'
            }
        },
        'powershell': {
            'name': 'PowerShell',
            'extensions': ['.ps1', '.psm1'],
            'interpreter': ['powershell', '-ExecutionPolicy', 'Bypass', '-File'],
            'comment': '#',
            'keywords': ['function', 'param', 'if', 'else', 'foreach', 'while', 'try', 'catch'],
            'syntax_colors': {
                'keywords': '#0000FF',
                'strings': '#008000',
                'comments': '#808080',
                'numbers': '#FF4500'
            }
        },
        'bash': {
            'name': 'Bash',
            'extensions': ['.sh', '.bash'],
            'interpreter': ['bash'] if os.name != 'nt' else ['wsl', 'bash'],
            'comment': '#',
            'keywords': ['function', 'if', 'then', 'else', 'fi', 'for', 'while', 'do', 'done'],
            'syntax_colors': {
                'keywords': '#0000FF',
                'strings': '#008000',
                'comments': '#808080',
                'numbers': '#FF4500'
            }
        },
        'cmd': {
            'name': 'Command Prompt',
            'extensions': ['.bat', '.cmd'],
            'interpreter': ['cmd', '/c'],
            'comment': 'REM',
            'keywords': ['echo', 'set', 'if', 'else', 'for', 'goto', 'call'],
            'syntax_colors': {
                'keywords': '#0000FF',
                'strings': '#008000',
                'comments': '#808080',
                'numbers': '#FF4500'
            }
        },
        'javascript': {
            'name': 'JavaScript (Node.js)',
            'extensions': ['.js', '.mjs'],
            'interpreter': ['node'],
            'comment': '//',
            'keywords': ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'try', 'catch'],
            'syntax_colors': {
                'keywords': '#0000FF',
                'strings': '#008000',
                'comments': '#808080',
                'numbers': '#FF4500'
            }
        },
        'ruby': {
            'name': 'Ruby',
            'extensions': ['.rb'],
            'interpreter': ['ruby'],
            'comment': '#',
            'keywords': ['def', 'class', 'module', 'if', 'else', 'elsif', 'end', 'for', 'while'],
            'syntax_colors': {
                'keywords': '#0000FF',
                'strings': '#008000',
                'comments': '#808080',
                'numbers': '#FF4500'
            }
        }
    }


class MCPInterface:
    """Interface for MCP (Model Context Protocol) tool integration"""
    
    def __init__(self, editor_instance):
        self.editor = editor_instance
        self.mcp_inputs = {}
        self.mcp_outputs = {}
        
    def register_input_handler(self, tool_name: str, handler: Callable):
        """Register an input handler for MCP tools"""
        self.mcp_inputs[tool_name] = handler
        
    def register_output_handler(self, tool_name: str, handler: Callable):
        """Register an output handler for MCP tools"""
        self.mcp_outputs[tool_name] = handler
        
    def send_to_mcp_tool(self, tool_name: str, data: Dict) -> Dict:
        """Send data to an MCP tool and return the response"""
        if tool_name in self.mcp_inputs:
            try:
                return self.mcp_inputs[tool_name](data)
            except Exception as e:
                return {"error": str(e)}
        return {"error": f"Tool '{tool_name}' not registered"}
        
    def receive_from_mcp_tool(self, tool_name: str, data: Dict):
        """Receive data from an MCP tool"""
        if tool_name in self.mcp_outputs:
            self.mcp_outputs[tool_name](data)
        else:
            # Default: insert into editor
            self.editor.insert_text(json.dumps(data, indent=2))


class SyntaxHighlighter:
    """Basic syntax highlighting for the text editor"""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.current_language = None
        self.setup_tags()
        
    def setup_tags(self):
        """Setup text tags for syntax highlighting"""
        self.text_widget.tag_configure("keyword", foreground="#0000FF", font=("Consolas", 10, "bold"))
        self.text_widget.tag_configure("string", foreground="#008000")
        self.text_widget.tag_configure("comment", foreground="#808080", font=("Consolas", 10, "italic"))
        self.text_widget.tag_configure("number", foreground="#FF4500")
        
    def highlight(self, language: str):
        """Apply syntax highlighting for the specified language"""
        if language not in LanguageConfig.LANGUAGES:
            return
            
        self.current_language = language
        lang_config = LanguageConfig.LANGUAGES[language]
        
        # Clear existing tags
        for tag in ["keyword", "string", "comment", "number"]:
            self.text_widget.tag_remove(tag, "1.0", tk.END)
            
        content = self.text_widget.get("1.0", tk.END)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_start = f"{line_num}.0"
            
            # Highlight comments
            comment_start = line.find(lang_config['comment'])
            if comment_start != -1:
                comment_pos = f"{line_num}.{comment_start}"
                comment_end = f"{line_num}.end"
                self.text_widget.tag_add("comment", comment_pos, comment_end)
                continue
                
            # Highlight keywords
            for keyword in lang_config['keywords']:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                for match in re.finditer(pattern, line):
                    start_pos = f"{line_num}.{match.start()}"
                    end_pos = f"{line_num}.{match.end()}"
                    self.text_widget.tag_add("keyword", start_pos, end_pos)
                    
            # Highlight strings
            string_patterns = [r'"[^"]*"', r"'[^']*'"]
            for pattern in string_patterns:
                for match in re.finditer(pattern, line):
                    start_pos = f"{line_num}.{match.start()}"
                    end_pos = f"{line_num}.{match.end()}"
                    self.text_widget.tag_add("string", start_pos, end_pos)
                    
            # Highlight numbers
            number_pattern = r'\b\d+\.?\d*\b'
            for match in re.finditer(number_pattern, line):
                start_pos = f"{line_num}.{match.start()}"
                end_pos = f"{line_num}.{match.end()}"
                self.text_widget.tag_add("number", start_pos, end_pos)


class ScriptExecutor:
    """Handles script execution in separate threads"""
    
    def __init__(self, output_callback: Callable[[str], None]):
        self.output_callback = output_callback
        self.current_process = None
        
    def execute_script(self, language: str, script_content: str, working_dir: str = None):
        """Execute script in a separate thread"""
        if language not in LanguageConfig.LANGUAGES:
            self.output_callback(f"Error: Language '{language}' not supported\n")
            return
            
        thread = threading.Thread(
            target=self._run_script,
            args=(language, script_content, working_dir),
            daemon=True
        )
        thread.start()
        
    def _run_script(self, language: str, script_content: str, working_dir: str = None):
        """Internal method to run the script"""
        lang_config = LanguageConfig.LANGUAGES[language]
        
        try:
            # Create temporary file for script
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=lang_config['extensions'][0],
                delete=False,
                encoding='utf-8'
            ) as temp_file:
                temp_file.write(script_content)
                temp_file_path = temp_file.name
                
            # Prepare command
            cmd = lang_config['interpreter'] + [temp_file_path]
            
            self.output_callback(f"Executing: {' '.join(cmd)}\n")
            self.output_callback("-" * 50 + "\n")
            
            # Execute script
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=working_dir or os.getcwd(),
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output in real-time
            while True:
                output = self.current_process.stdout.readline()
                if output == '' and self.current_process.poll() is not None:
                    break
                if output:
                    self.output_callback(output)
                    
            # Get any remaining output
            stdout, stderr = self.current_process.communicate()
            if stdout:
                self.output_callback(stdout)
            if stderr:
                self.output_callback(f"STDERR:\n{stderr}")
                
            return_code = self.current_process.returncode
            self.output_callback(f"\nProcess finished with return code: {return_code}\n")
            self.output_callback("=" * 50 + "\n")
            
        except Exception as e:
            self.output_callback(f"Execution error: {str(e)}\n")
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
            self.current_process = None
            
    def terminate_execution(self):
        """Terminate the currently running process"""
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            self.output_callback("\nExecution terminated by user.\n")


class MultiLanguageScriptEditor:
    """Main application class for the multi-language script editor"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Multi-Language Script Editor with MCP Integration")
        self.root.geometry("1200x800")
        
        # Application state
        self.current_file = None
        self.current_language = 'python'
        self.modified = False
        
        # Initialize components
        self.setup_ui()
        self.setup_menu()
        self.highlighter = SyntaxHighlighter(self.text_editor)
        self.executor = ScriptExecutor(self.append_output)
        self.mcp_interface = MCPInterface(self)
        
        # Setup event bindings
        self.setup_bindings()
        
        # Load default template
        self.load_template('python')
        
    def setup_ui(self):
        """Setup the user interface"""
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Editor
        editor_frame = ttk.Frame(main_paned)
        main_paned.add(editor_frame, weight=7)
        
        # Editor toolbar
        toolbar_frame = ttk.Frame(editor_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Language selector
        ttk.Label(toolbar_frame, text="Language:").pack(side=tk.LEFT, padx=(0, 5))
        self.language_var = tk.StringVar(value='python')
        self.language_combo = ttk.Combobox(
            toolbar_frame,
            textvariable=self.language_var,
            values=list(LanguageConfig.LANGUAGES.keys()),
            state="readonly",
            width=15
        )
        self.language_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_changed)
        
        # Control buttons
        ttk.Button(toolbar_frame, text="Run", command=self.run_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Stop", command=self.stop_execution).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT, padx=2)
        
        # File info label
        self.file_info_var = tk.StringVar(value="New File")
        ttk.Label(toolbar_frame, textvariable=self.file_info_var).pack(side=tk.RIGHT)
        
        # Text editor with line numbers
        editor_container = ttk.Frame(editor_frame)
        editor_container.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers (simplified)
        self.line_numbers = tk.Text(
            editor_container,
            width=4,
            height=1,
            bg='#f0f0f0',
            fg='#666666',
            state=tk.DISABLED,
            font=("Consolas", 10)
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main text editor
        self.text_editor = scrolledtext.ScrolledText(
            editor_container,
            wrap=tk.NONE,
            font=("Consolas", 10),
            undo=True,
            maxundo=50
        )
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right panel - Output and MCP Interface
        right_panel = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_panel, weight=3)
        
        # Output panel
        output_frame = ttk.LabelFrame(right_panel, text="Output")
        right_panel.add(output_frame, weight=6)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg='#2d2d2d',
            fg='#ffffff',
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # MCP Interface panel
        mcp_frame = ttk.LabelFrame(right_panel, text="MCP Tool Interface")
        right_panel.add(mcp_frame, weight=4)
        
        # MCP Input
        ttk.Label(mcp_frame, text="MCP Input:").pack(anchor=tk.W, padx=5, pady=(5, 0))
        self.mcp_input = scrolledtext.ScrolledText(
            mcp_frame,
            height=6,
            font=("Consolas", 9)
        )
        self.mcp_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # MCP Controls
        mcp_controls = ttk.Frame(mcp_frame)
        mcp_controls.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(mcp_controls, text="Tool:").pack(side=tk.LEFT)
        self.mcp_tool_var = tk.StringVar(value="example_tool")
        mcp_tool_entry = ttk.Entry(mcp_controls, textvariable=self.mcp_tool_var, width=15)
        mcp_tool_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(mcp_controls, text="Send to MCP", command=self.send_to_mcp).pack(side=tk.LEFT, padx=2)
        ttk.Button(mcp_controls, text="Insert Response", command=self.insert_mcp_response).pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_menu(self):
        """Setup the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=lambda: self.text_editor.edit_undo(), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=lambda: self.text_editor.edit_redo(), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.text_editor.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self.text_editor.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self.text_editor.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Script", command=self.run_script, accelerator="F5")
        run_menu.add_command(label="Stop Execution", command=self.stop_execution, accelerator="Ctrl+Break")
        
        # Templates menu
        templates_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Templates", menu=templates_menu)
        for lang in LanguageConfig.LANGUAGES:
            templates_menu.add_command(
                label=f"Load {LanguageConfig.LANGUAGES[lang]['name']} Template",
                command=lambda l=lang: self.load_template(l)
            )
            
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def setup_bindings(self):
        """Setup keyboard bindings and event handlers"""
        # File operations
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_file_as())
        
        # Run script
        self.root.bind('<F5>', lambda e: self.run_script())
        
        # Text modification tracking
        self.text_editor.bind('<KeyPress>', self.on_text_modified)
        self.text_editor.bind('<Button-1>', self.update_line_numbers)
        self.text_editor.bind('<KeyRelease>', self.update_line_numbers)
        
    def on_language_changed(self, event=None):
        """Handle language selection change"""
        self.current_language = self.language_var.get()
        self.highlighter.highlight(self.current_language)
        self.update_status(f"Language changed to {LanguageConfig.LANGUAGES[self.current_language]['name']}")
        
    def on_text_modified(self, event=None):
        """Handle text modification"""
        self.modified = True
        self.update_title()
        
    def update_line_numbers(self, event=None):
        """Update line numbers display"""
        # Simplified line numbering
        content = self.text_editor.get("1.0", tk.END)
        line_count = content.count('\n')
        
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i:3d}\n")
            
        self.line_numbers.config(state=tk.DISABLED)
        
    def update_title(self):
        """Update window title"""
        title = "Multi-Language Script Editor with MCP Integration"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.modified:
            title += " *"
        self.root.title(title)
        
    def update_status(self, message: str):
        """Update status bar"""
        self.status_bar.config(text=message)
        
    def new_file(self):
        """Create a new file"""
        if self.modified and not self.confirm_discard_changes():
            return
            
        self.text_editor.delete("1.0", tk.END)
        self.current_file = None
        self.modified = False
        self.file_info_var.set("New File")
        self.update_title()
        self.clear_output()
        
    def open_file(self):
        """Open an existing file"""
        if self.modified and not self.confirm_discard_changes():
            return
            
        file_path = filedialog.askopenfilename(
            title="Open Script File",
            filetypes=[
                ("All Script Files", "*.py;*.ps1;*.sh;*.bat;*.cmd;*.js;*.rb"),
                ("Python Files", "*.py;*.pyw"),
                ("PowerShell Files", "*.ps1;*.psm1"),
                ("Shell Scripts", "*.sh;*.bash"),
                ("Batch Files", "*.bat;*.cmd"),
                ("JavaScript Files", "*.js;*.mjs"),
                ("Ruby Files", "*.rb"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert("1.0", content)
                
                self.current_file = file_path
                self.modified = False
                
                # Auto-detect language from extension
                ext = os.path.splitext(file_path)[1].lower()
                for lang, config in LanguageConfig.LANGUAGES.items():
                    if ext in config['extensions']:
                        self.language_var.set(lang)
                        self.current_language = lang
                        break
                        
                self.file_info_var.set(os.path.basename(file_path))
                self.update_title()
                self.highlighter.highlight(self.current_language)
                self.update_line_numbers()
                self.update_status(f"Loaded: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")
                
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Save the file with a new name"""
        ext = LanguageConfig.LANGUAGES[self.current_language]['extensions'][0]
        default_name = f"script{ext}"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Script File",
            defaultextension=ext,
            initialvalue=default_name,
            filetypes=[
                (f"{LanguageConfig.LANGUAGES[self.current_language]['name']} Files", f"*{ext}"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self._save_to_file(file_path)
            
    def _save_to_file(self, file_path: str):
        """Internal method to save file"""
        try:
            content = self.text_editor.get("1.0", tk.END + "-1c")  # Exclude final newline
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
                
            self.current_file = file_path
            self.modified = False
            self.file_info_var.set(os.path.basename(file_path))
            self.update_title()
            self.update_status(f"Saved: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
            
    def confirm_discard_changes(self) -> bool:
        """Ask user to confirm discarding unsaved changes"""
        result = messagebox.askyesnocancel(
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save them?",
            icon='warning'
        )
        
        if result is True:  # Yes - save first
            self.save_file()
            return not self.modified  # Return True if save succeeded
        elif result is False:  # No - discard changes
            return True
        else:  # Cancel
            return False
            
    def load_template(self, language: str):
        """Load a template for the specified language"""
        templates = {
            'python': '''#!/usr/bin/env python3
"""
Python Script Template
"""

def main():
    print("Hello from Python!")
    
    # MCP Tool integration example
    # You can use the MCP interface to send/receive data
    
    # Example: Send data to MCP tool
    # (Use the MCP Interface panel on the right)
    
if __name__ == "__main__":
    main()
''',
            'powershell': '''# PowerShell Script Template

Write-Host "Hello from PowerShell!"

# MCP Tool integration example
# You can use the MCP interface to send/receive data

# Example function
function Get-SystemInfo {
    Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory
}

Get-SystemInfo
''',
            'bash': '''#!/bin/bash
# Bash Script Template

echo "Hello from Bash!"

# MCP Tool integration example
# You can use the MCP interface to send/receive data

# Example function
show_system_info() {
    echo "System Information:"
    uname -a
    echo "Current directory: $(pwd)"
}

show_system_info
''',
            'cmd': '''@echo off
REM Command Prompt Script Template

echo Hello from Command Prompt!

REM MCP Tool integration example
REM You can use the MCP interface to send/receive data

echo System Information:
systeminfo | findstr "OS Name"
echo Current directory: %CD%
''',
            'javascript': '''// JavaScript (Node.js) Script Template

console.log("Hello from JavaScript!");

// MCP Tool integration example
// You can use the MCP interface to send/receive data

function showSystemInfo() {
    console.log("Node.js version:", process.version);
    console.log("Platform:", process.platform);
    console.log("Current directory:", process.cwd());
}

showSystemInfo();
''',
            'ruby': '''#!/usr/bin/env ruby
# Ruby Script Template

puts "Hello from Ruby!"

# MCP Tool integration example
# You can use the MCP interface to send/receive data

def show_system_info
    puts "Ruby version: #{RUBY_VERSION}"
    puts "Platform: #{RUBY_PLATFORM}"
    puts "Current directory: #{Dir.pwd}"
end

show_system_info
'''
        }
        
        if language in templates:
            if self.modified and not self.confirm_discard_changes():
                return
                
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert("1.0", templates[language])
            self.language_var.set(language)
            self.current_language = language
            self.current_file = None
            self.modified = False
            self.file_info_var.set(f"Template - {LanguageConfig.LANGUAGES[language]['name']}")
            self.update_title()
            self.highlighter.highlight(language)
            self.update_line_numbers()
            self.clear_output()
            
    def run_script(self):
        """Execute the current script"""
        content = self.text_editor.get("1.0", tk.END + "-1c")
        if not content.strip():
            messagebox.showwarning("Warning", "No script content to execute.")
            return
            
        self.clear_output()
        working_dir = None
        if self.current_file:
            working_dir = os.path.dirname(self.current_file)
            
        self.executor.execute_script(self.current_language, content, working_dir)
        self.update_status(f"Executing {LanguageConfig.LANGUAGES[self.current_language]['name']} script...")
        
    def stop_execution(self):
        """Stop the currently running script"""
        self.executor.terminate_execution()
        self.update_status("Execution stopped.")
        
    def append_output(self, text: str):
        """Append text to the output panel"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        
    def clear_output(self):
        """Clear the output panel"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        
    def send_to_mcp(self):
        """Send data to MCP tool"""
        tool_name = self.mcp_tool_var.get().strip()
        if not tool_name:
            messagebox.showwarning("Warning", "Please specify a tool name.")
            return
            
        try:
            mcp_content = self.mcp_input.get("1.0", tk.END + "-1c")
            if not mcp_content.strip():
                data = {"script_content": self.text_editor.get("1.0", tk.END + "-1c")}
            else:
                data = json.loads(mcp_content) if mcp_content.strip().startswith('{') else {"text": mcp_content}
                
            response = self.mcp_interface.send_to_mcp_tool(tool_name, data)
            self.append_output(f"MCP Tool '{tool_name}' Response:\n{json.dumps(response, indent=2)}\n")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON in MCP input:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"MCP communication error:\n{str(e)}")
            
    def insert_mcp_response(self):
        """Insert MCP response into the editor"""
        # This is a placeholder for MCP response insertion
        # In a real implementation, this would get the last MCP response
        sample_response = '''# MCP Tool Response
# This is where MCP tool responses would be inserted
print("Response from MCP tool")
'''
        cursor_pos = self.text_editor.index(tk.INSERT)
        self.text_editor.insert(cursor_pos, sample_response)
        
    def insert_text(self, text: str):
        """Insert text at the current cursor position"""
        cursor_pos = self.text_editor.index(tk.INSERT)
        self.text_editor.insert(cursor_pos, text)
        self.modified = True
        self.update_title()
        
    def show_about(self):
        """Show about dialog"""
        about_text = """Multi-Language Script Editor with MCP Integration

Version: 1.0
Author: AI Assistant

Features:
• Multi-language script editing and execution
• Syntax highlighting
• MCP (Model Context Protocol) tool integration
• Cross-platform compatibility
• File operations (New, Open, Save)
• Script templates

Supported Languages:
• Python
• PowerShell
• Bash
• Command Prompt (Batch)
• JavaScript (Node.js)
• Ruby

This editor is designed to work with MCP tools for
enhanced automation and integration capabilities.
"""
        messagebox.showinfo("About", about_text)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        app = MultiLanguageScriptEditor()
        app.run()
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()