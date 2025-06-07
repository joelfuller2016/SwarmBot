"""
Tool Browser UI Component
Displays available MCP tools and their documentation
"""

from .base import UIComponent
import tkinter as tk
from tkinter import ttk, scrolledtext


class ToolBrowser(UIComponent):
    """Tool browser for exploring available MCP tools"""
    
    def __init__(self, parent=None):
        """Initialize tool browser"""
        super().__init__(parent)
        self.tools = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the tool browser UI"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("MCP Tool Browser")
        self.window.geometry("800x600")
        
        # Create main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tool list
        self.tool_listbox = tk.Listbox(main_frame, width=30)
        self.tool_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        self.tool_listbox.bind('<<ListboxSelect>>', self.on_tool_select)
        
        # Tool details
        self.details_text = scrolledtext.ScrolledText(main_frame, width=50, height=20)
        self.details_text.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Initially hide
        self.window.withdraw()
    
    def on_tool_select(self, event):
        """Handle tool selection"""
        selection = self.tool_listbox.curselection()
        if selection:
            tool_name = self.tool_listbox.get(selection[0])
            self.show_tool_details(tool_name)
    
    def show_tool_details(self, tool_name):
        """Display details for selected tool"""
        self.details_text.delete(1.0, tk.END)
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            details = f"Tool: {tool_name}\\n\\n"
            details += f"Description: {tool.get('description', 'No description')}\\n\\n"
            details += f"Parameters: {tool.get('parameters', {})}\\n"
            self.details_text.insert(1.0, details)
    
    def update_tools(self, tools):
        """Update the list of available tools"""
        self.tools = tools
        self.tool_listbox.delete(0, tk.END)
        for tool_name in sorted(tools.keys()):
            self.tool_listbox.insert(tk.END, tool_name)
    
    def show(self):
        """Show the tool browser window"""
        self.window.deiconify()
        self.window.lift()
    
    def hide(self):
        """Hide the tool browser window"""
        self.window.withdraw()
    
    def destroy(self):
        """Destroy the tool browser window"""
        self.window.destroy()
