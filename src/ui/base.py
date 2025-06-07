"""
Base UI Framework for SwarmBot
Provides the foundation for all UI components
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
from typing import Dict, Any, Optional, Callable, List
from abc import ABC, abstractmethod
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class UIComponent(ABC):
    """Abstract base class for all UI components"""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.config = kwargs
        self.callbacks: Dict[str, List[Callable]] = {}
        
    @abstractmethod
    def build(self) -> None:
        """Build the UI component"""
        pass
    
    def pack(self, **kwargs) -> None:
        """Pack the component frame"""
        self.frame.pack(**kwargs)
        
    def grid(self, **kwargs) -> None:
        """Grid the component frame"""
        self.frame.grid(**kwargs)
        
    def place(self, **kwargs) -> None:
        """Place the component frame"""
        self.frame.place(**kwargs)
        
    def bind_event(self, event: str, callback: Callable) -> None:
        """Bind an event callback"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
        
    def trigger_event(self, event: str, *args, **kwargs) -> None:
        """Trigger an event"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}")
                    
    def update_config(self, **kwargs) -> None:
        """Update component configuration"""
        self.config.update(kwargs)
        self.refresh()
        
    def refresh(self) -> None:
        """Refresh the component (override in subclasses)"""
        pass


class SwarmBotUI:
    """Main UI application for SwarmBot"""
    
    def __init__(self, title: str = "SwarmBot - AI Assistant Hub"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("1200x800")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Application state
        self.config_file = Path.home() / ".swarmbot" / "ui_config.json"
        self.config = self.load_config()
        self.components: Dict[str, UIComponent] = {}
        self.async_loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Setup UI
        self.setup_window()
        self.create_menu()
        self.create_layout()
        
    def load_config(self) -> Dict[str, Any]:
        """Load UI configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "theme": "dark",
            "window": {
                "width": 1200,
                "height": 800,
                "x": None,
                "y": None
            },
            "panels": {
                "chat": {"visible": True, "width": 600},
                "servers": {"visible": True, "width": 300},
                "tools": {"visible": True, "height": 200},
                "config": {"visible": False}
            },
            "preferences": {
                "auto_connect": True,
                "show_timestamps": True,
                "notification_sound": True,
                "log_level": "INFO"
            }
        }
    
    def save_config(self) -> None:
        """Save UI configuration"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def setup_window(self) -> None:
        """Setup main window properties"""
        # Set window icon (if available)
        try:
            icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        # Configure window position
        if self.config["window"]["x"] and self.config["window"]["y"]:
            self.root.geometry(
                f"{self.config['window']['width']}x{self.config['window']['height']}"
                f"+{self.config['window']['x']}+{self.config['window']['y']}"
            )
        
        # Bind window events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Configure>", self.on_window_configure)
        
    def create_menu(self) -> None:
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Session", command=self.new_session)
        file_menu.add_command(label="Load Session", command=self.load_session)
        file_menu.add_command(label="Save Session", command=self.save_session)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V")
        edit_menu.add_command(label="Clear Chat", command=self.clear_chat)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Server Panel", 
                                  variable=tk.BooleanVar(value=self.config["panels"]["servers"]["visible"]),
                                  command=lambda: self.toggle_panel("servers"))
        view_menu.add_checkbutton(label="Tool Browser",
                                  variable=tk.BooleanVar(value=self.config["panels"]["tools"]["visible"]),
                                  command=lambda: self.toggle_panel("tools"))
        view_menu.add_separator()
        view_menu.add_command(label="Themes", command=self.show_theme_selector)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Tool Browser", command=self.show_tool_browser)
        tools_menu.add_command(label="Server Manager", command=self.show_server_manager)
        tools_menu.add_separator()
        tools_menu.add_command(label="Task Planner", command=self.show_task_planner)
        tools_menu.add_command(label="Code Generator", command=self.show_code_generator)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_docs)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_layout(self) -> None:
        """Create the main UI layout"""
        # Create main paned window
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (servers/navigation)
        self.left_frame = ttk.Frame(self.main_paned, width=300)
        self.main_paned.add(self.left_frame, weight=0)
        
        # Center panel (chat)
        self.center_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.center_frame, weight=1)
        
        # Right panel (tools/info)
        self.right_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.right_paned, weight=0)
        
        # Status bar
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(self.status_bar, mode='indeterminate', length=100)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        
    def add_component(self, name: str, component: UIComponent) -> None:
        """Add a UI component"""
        self.components[name] = component
        component.build()
        
    def get_component(self, name: str) -> Optional[UIComponent]:
        """Get a UI component by name"""
        return self.components.get(name)
        
    def toggle_panel(self, panel_name: str) -> None:
        """Toggle panel visibility"""
        if panel_name in self.config["panels"]:
            self.config["panels"][panel_name]["visible"] = not self.config["panels"][panel_name]["visible"]
            self.refresh_layout()
            
    def refresh_layout(self) -> None:
        """Refresh the UI layout based on configuration"""
        # Implementation depends on specific panel arrangements
        pass
        
    def set_status(self, message: str, duration: int = 0) -> None:
        """Set status bar message"""
        self.status_label.config(text=message)
        if duration > 0:
            self.root.after(duration * 1000, lambda: self.status_label.config(text="Ready"))
            
    def show_progress(self, show: bool = True) -> None:
        """Show/hide progress indicator"""
        if show:
            self.progress_bar.start(10)
        else:
            self.progress_bar.stop()
            
    def run_async(self, coro) -> None:
        """Run an async coroutine in the UI thread"""
        if self.async_loop:
            asyncio.run_coroutine_threadsafe(coro, self.async_loop)
            
    # Menu command implementations
    def new_session(self) -> None:
        """Start a new chat session"""
        if messagebox.askyesno("New Session", "Start a new session? Current session will be cleared."):
            if "chat" in self.components:
                self.components["chat"].clear()
                
    def load_session(self) -> None:
        """Load a saved session"""
        # Implementation for session loading
        pass
        
    def save_session(self) -> None:
        """Save current session"""
        # Implementation for session saving
        pass
        
    def show_settings(self) -> None:
        """Show settings dialog"""
        if "config" in self.components:
            self.components["config"].show()
            
    def clear_chat(self) -> None:
        """Clear chat history"""
        if "chat" in self.components:
            self.components["chat"].clear()
            
    def show_theme_selector(self) -> None:
        """Show theme selection dialog"""
        if "theme_manager" in self.components:
            self.components["theme_manager"].show_selector()
            
    def show_tool_browser(self) -> None:
        """Show tool browser"""
        if "tool_browser" in self.components:
            self.components["tool_browser"].show()
            
    def show_server_manager(self) -> None:
        """Show server manager"""
        if "server_manager" in self.components:
            self.components["server_manager"].show()
            
    def show_task_planner(self) -> None:
        """Show task planner"""
        messagebox.showinfo("Task Planner", "Task planner coming soon!")
        
    def show_code_generator(self) -> None:
        """Show code generator"""
        messagebox.showinfo("Code Generator", "Code generator coming soon!")
        
    def show_docs(self) -> None:
        """Show documentation"""
        import webbrowser
        webbrowser.open("https://github.com/yourusername/SwarmBot/wiki")
        
    def show_shortcuts(self) -> None:
        """Show keyboard shortcuts"""
        shortcuts = """
        Keyboard Shortcuts:
        
        Ctrl+N - New Session
        Ctrl+O - Open Session
        Ctrl+S - Save Session
        Ctrl+Enter - Send Message
        Ctrl+L - Clear Chat
        Ctrl+, - Settings
        F1 - Help
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
        
    def show_about(self) -> None:
        """Show about dialog"""
        about_text = """
        SwarmBot UI
        Version 1.0.0
        
        A comprehensive AI assistant with multiple MCP server integrations.
        
        © 2025 SwarmBot Team
        """
        messagebox.showinfo("About SwarmBot", about_text)
        
    def on_window_configure(self, event) -> None:
        """Handle window configuration changes"""
        if event.widget == self.root:
            self.config["window"]["width"] = self.root.winfo_width()
            self.config["window"]["height"] = self.root.winfo_height()
            self.config["window"]["x"] = self.root.winfo_x()
            self.config["window"]["y"] = self.root.winfo_y()
            
    def on_closing(self) -> None:
        """Handle window closing"""
        self.save_config()
        self.root.quit()
        
    def run(self) -> None:
        """Run the UI application"""
        self.root.mainloop()
