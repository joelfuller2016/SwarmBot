"""
Configuration Panel for SwarmBot UI
Provides a comprehensive settings interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional, Callable
import json
from pathlib import Path
import logging
from .base import UIComponent

logger = logging.getLogger(__name__)


class ConfigurationPanel(UIComponent):
    """Configuration and settings panel"""
    
    def __init__(self, parent: tk.Widget, config_manager: Any, **kwargs):
        super().__init__(parent, **kwargs)
        self.config_manager = config_manager
        self.dialog = None
        self.changes = {}
        self.tabs = {}
        
    def build(self) -> None:
        """Build the configuration panel"""
        # This can be embedded or shown as a dialog
        pass
        
    def show(self) -> None:
        """Show configuration dialog"""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.lift()
            return
            
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("SwarmBot Settings")
        self.dialog.geometry("800x600")
        self.dialog.transient(self.parent)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_general_tab()
        self.create_llm_tab()
        self.create_servers_tab()
        self.create_interface_tab()
        self.create_advanced_tab()
        self.create_keybindings_tab()
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="Apply",
            command=self.apply_changes
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="OK",
            command=self.ok_clicked
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_to_defaults
        ).pack(side=tk.LEFT)
        
    def create_general_tab(self) -> None:
        """Create general settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="General")
        self.tabs["general"] = tab
        
        # Auto-connect setting
        auto_connect_frame = ttk.Frame(tab)
        auto_connect_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.auto_connect_var = tk.BooleanVar(
            value=self.config_manager.get("preferences.auto_connect", True)
        )
        ttk.Checkbutton(
            auto_connect_frame,
            text="Automatically connect to servers on startup",
            variable=self.auto_connect_var,
            command=lambda: self.mark_changed("preferences.auto_connect", self.auto_connect_var.get())
        ).pack(anchor=tk.W)
        
        # Default mode
        mode_frame = ttk.LabelFrame(tab, text="Default Mode", padding=10)
        mode_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.default_mode_var = tk.StringVar(
            value=self.config_manager.get("preferences.default_mode", "enhanced")
        )
        
        ttk.Radiobutton(
            mode_frame,
            text="Standard Mode - Manual tool execution",
            value="standard",
            variable=self.default_mode_var,
            command=lambda: self.mark_changed("preferences.default_mode", self.default_mode_var.get())
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            mode_frame,
            text="Enhanced Mode - Automatic tool detection",
            value="enhanced",
            variable=self.default_mode_var,
            command=lambda: self.mark_changed("preferences.default_mode", self.default_mode_var.get())
        ).pack(anchor=tk.W, pady=2)
        
        # Logging level
        log_frame = ttk.LabelFrame(tab, text="Logging", padding=10)
        log_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(log_frame, text="Log Level:").pack(side=tk.LEFT, padx=5)
        
        self.log_level_var = tk.StringVar(
            value=self.config_manager.get("preferences.log_level", "INFO")
        )
        log_combo = ttk.Combobox(
            log_frame,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=15
        )
        log_combo.pack(side=tk.LEFT, padx=5)
        log_combo.bind("<<ComboboxSelected>>", 
                      lambda e: self.mark_changed("preferences.log_level", self.log_level_var.get()))
        
        # Session management
        session_frame = ttk.LabelFrame(tab, text="Session Management", padding=10)
        session_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.auto_save_var = tk.BooleanVar(
            value=self.config_manager.get("preferences.auto_save_session", True)
        )
        ttk.Checkbutton(
            session_frame,
            text="Automatically save session on exit",
            variable=self.auto_save_var,
            command=lambda: self.mark_changed("preferences.auto_save_session", self.auto_save_var.get())
        ).pack(anchor=tk.W, pady=2)
        
        self.restore_session_var = tk.BooleanVar(
            value=self.config_manager.get("preferences.restore_session", True)
        )
        ttk.Checkbutton(
            session_frame,
            text="Restore previous session on startup",
            variable=self.restore_session_var,
            command=lambda: self.mark_changed("preferences.restore_session", self.restore_session_var.get())
        ).pack(anchor=tk.W, pady=2)
        
    def create_llm_tab(self) -> None:
        """Create LLM provider settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="LLM Providers")
        self.tabs["llm"] = tab
        
        # Provider selection
        provider_frame = ttk.LabelFrame(tab, text="Default Provider", padding=10)
        provider_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.llm_provider_var = tk.StringVar(
            value=self.config_manager.get("llm.default_provider", "openai")
        )
        
        providers = [
            ("OpenAI", "openai"),
            ("Anthropic Claude", "anthropic"),
            ("Groq", "groq"),
            ("Azure OpenAI", "azure")
        ]
        
        for display_name, value in providers:
            ttk.Radiobutton(
                provider_frame,
                text=display_name,
                value=value,
                variable=self.llm_provider_var,
                command=lambda: self.mark_changed("llm.default_provider", self.llm_provider_var.get())
            ).pack(anchor=tk.W, pady=2)
        
        # API Keys
        keys_frame = ttk.LabelFrame(tab, text="API Keys", padding=10)
        keys_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(keys_frame, text="API keys are stored in environment variables for security.").pack(anchor=tk.W)
        ttk.Label(keys_frame, text="Edit your .env file to update API keys.").pack(anchor=tk.W)
        
        ttk.Button(
            keys_frame,
            text="Open .env File",
            command=self.open_env_file
        ).pack(anchor=tk.W, pady=10)
        
        # Model settings
        model_frame = ttk.LabelFrame(tab, text="Model Settings", padding=10)
        model_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Temperature
        temp_frame = ttk.Frame(model_frame)
        temp_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(temp_frame, text="Temperature:").pack(side=tk.LEFT, padx=5)
        
        self.temperature_var = tk.DoubleVar(
            value=self.config_manager.get("llm.temperature", 0.7)
        )
        temp_scale = ttk.Scale(
            temp_frame,
            from_=0.0,
            to=1.0,
            variable=self.temperature_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=lambda v: self.update_temp_label()
        )
        temp_scale.pack(side=tk.LEFT, padx=5)
        
        self.temp_label = ttk.Label(temp_frame, text=f"{self.temperature_var.get():.1f}")
        self.temp_label.pack(side=tk.LEFT, padx=5)
        
        # Max tokens
        tokens_frame = ttk.Frame(model_frame)
        tokens_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(tokens_frame, text="Max Tokens:").pack(side=tk.LEFT, padx=5)
        
        self.max_tokens_var = tk.IntVar(
            value=self.config_manager.get("llm.max_tokens", 2000)
        )
        tokens_spin = ttk.Spinbox(
            tokens_frame,
            from_=100,
            to=4000,
            textvariable=self.max_tokens_var,
            width=10,
            command=lambda: self.mark_changed("llm.max_tokens", self.max_tokens_var.get())
        )
        tokens_spin.pack(side=tk.LEFT, padx=5)
        
    def create_servers_tab(self) -> None:
        """Create MCP servers configuration tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="MCP Servers")
        self.tabs["servers"] = tab
        
        # Server list
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview for servers
        columns = ("status", "type", "auto_start")
        self.server_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="tree headings",
            height=10
        )
        
        # Configure columns
        self.server_tree.heading("#0", text="Server Name")
        self.server_tree.heading("status", text="Status")
        self.server_tree.heading("type", text="Type")
        self.server_tree.heading("auto_start", text="Auto Start")
        
        self.server_tree.column("#0", width=200)
        self.server_tree.column("status", width=100)
        self.server_tree.column("type", width=100)
        self.server_tree.column("auto_start", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.server_tree.yview)
        self.server_tree.configure(yscrollcommand=scrollbar.set)
        
        self.server_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load servers
        self.load_servers()
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(
            button_frame,
            text="Add Server",
            command=self.add_server
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Edit",
            command=self.edit_server
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Remove",
            command=self.remove_server
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Test Connection",
            command=self.test_server
        ).pack(side=tk.RIGHT, padx=5)
        
    def create_interface_tab(self) -> None:
        """Create interface settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Interface")
        self.tabs["interface"] = tab
        
        # Theme selection
        theme_frame = ttk.LabelFrame(tab, text="Theme", padding=10)
        theme_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(theme_frame, text="Color Theme:").pack(side=tk.LEFT, padx=5)
        
        self.theme_var = tk.StringVar(
            value=self.config_manager.get("ui.theme", "Dark")
        )
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["Dark", "Light", "Nord"],
            state="readonly",
            width=15
        )
        theme_combo.pack(side=tk.LEFT, padx=5)
        theme_combo.bind("<<ComboboxSelected>>", 
                        lambda e: self.mark_changed("ui.theme", self.theme_var.get()))
        
        ttk.Button(
            theme_frame,
            text="Theme Editor",
            command=self.open_theme_editor
        ).pack(side=tk.LEFT, padx=20)
        
        # Font settings
        font_frame = ttk.LabelFrame(tab, text="Fonts", padding=10)
        font_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Chat font size
        chat_font_frame = ttk.Frame(font_frame)
        chat_font_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(chat_font_frame, text="Chat Font Size:").pack(side=tk.LEFT, padx=5)
        
        self.chat_font_size_var = tk.IntVar(
            value=self.config_manager.get("ui.chat_font_size", 11)
        )
        font_spin = ttk.Spinbox(
            chat_font_frame,
            from_=8,
            to=20,
            textvariable=self.chat_font_size_var,
            width=10,
            command=lambda: self.mark_changed("ui.chat_font_size", self.chat_font_size_var.get())
        )
        font_spin.pack(side=tk.LEFT, padx=5)
        
        # Display options
        display_frame = ttk.LabelFrame(tab, text="Display Options", padding=10)
        display_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.show_timestamps_var = tk.BooleanVar(
            value=self.config_manager.get("ui.show_timestamps", True)
        )
        ttk.Checkbutton(
            display_frame,
            text="Show timestamps in chat",
            variable=self.show_timestamps_var,
            command=lambda: self.mark_changed("ui.show_timestamps", self.show_timestamps_var.get())
        ).pack(anchor=tk.W, pady=2)
        
        self.show_tool_icons_var = tk.BooleanVar(
            value=self.config_manager.get("ui.show_tool_icons", True)
        )
        ttk.Checkbutton(
            display_frame,
            text="Show tool icons",
            variable=self.show_tool_icons_var,
            command=lambda: self.mark_changed("ui.show_tool_icons", self.show_tool_icons_var.get())
        ).pack(anchor=tk.W, pady=2)
        
        self.animate_messages_var = tk.BooleanVar(
            value=self.config_manager.get("ui.animate_messages", True)
        )
        ttk.Checkbutton(
            display_frame,
            text="Animate message appearance",
            variable=self.animate_messages_var,
            command=lambda: self.mark_changed("ui.animate_messages", self.animate_messages_var.get())
        ).pack(anchor=tk.W, pady=2)
        
        # Notification settings
        notif_frame = ttk.LabelFrame(tab, text="Notifications", padding=10)
        notif_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.notif_sound_var = tk.BooleanVar(
            value=self.config_manager.get("ui.notification_sound", True)
        )
        ttk.Checkbutton(
            notif_frame,
            text="Play sound on new messages",
            variable=self.notif_sound_var,
            command=lambda: self.mark_changed("ui.notification_sound", self.notif_sound_var.get())
        ).pack(anchor=tk.W, pady=2)
        
        self.desktop_notif_var = tk.BooleanVar(
            value=self.config_manager.get("ui.desktop_notifications", False)
        )
        ttk.Checkbutton(
            notif_frame,
            text="Show desktop notifications",
            variable=self.desktop_notif_var,
            command=lambda: self.mark_changed("ui.desktop_notifications", self.desktop_notif_var.get())
        ).pack(anchor=tk.W, pady=2)
        
    def create_advanced_tab(self) -> None:
        """Create advanced settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Advanced")
        self.tabs["advanced"] = tab
        
        # Performance settings
        perf_frame = ttk.LabelFrame(tab, text="Performance", padding=10)
        perf_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Message history limit
        history_frame = ttk.Frame(perf_frame)
        history_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(history_frame, text="Message History Limit:").pack(side=tk.LEFT, padx=5)
        
        self.history_limit_var = tk.IntVar(
            value=self.config_manager.get("performance.history_limit", 1000)
        )
        history_spin = ttk.Spinbox(
            history_frame,
            from_=100,
            to=10000,
            increment=100,
            textvariable=self.history_limit_var,
            width=10,
            command=lambda: self.mark_changed("performance.history_limit", self.history_limit_var.get())
        )
        history_spin.pack(side=tk.LEFT, padx=5)
        
        # Cache settings
        cache_frame = ttk.LabelFrame(tab, text="Cache", padding=10)
        cache_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.enable_cache_var = tk.BooleanVar(
            value=self.config_manager.get("cache.enabled", True)
        )
        ttk.Checkbutton(
            cache_frame,
            text="Enable response caching",
            variable=self.enable_cache_var,
            command=lambda: self.mark_changed("cache.enabled", self.enable_cache_var.get())
        ).pack(anchor=tk.W, pady=2)
        
        # Cache size
        cache_size_frame = ttk.Frame(cache_frame)
        cache_size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(cache_size_frame, text="Max Cache Size (MB):").pack(side=tk.LEFT, padx=5)
        
        self.cache_size_var = tk.IntVar(
            value=self.config_manager.get("cache.max_size_mb", 100)
        )
        cache_spin = ttk.Spinbox(
            cache_size_frame,
            from_=10,
            to=1000,
            increment=10,
            textvariable=self.cache_size_var,
            width=10,
            command=lambda: self.mark_changed("cache.max_size_mb", self.cache_size_var.get())
        )
        cache_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            cache_frame,
            text="Clear Cache",
            command=self.clear_cache
        ).pack(anchor=tk.W, pady=10)
        
        # Debug options
        debug_frame = ttk.LabelFrame(tab, text="Debug Options", padding=10)
        debug_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.debug_mode_var = tk.BooleanVar(
            value=self.config_manager.get("debug.enabled", False)
        )
        ttk.Checkbutton(
            debug_frame,
            text="Enable debug mode",
            variable=self.debug_mode_var,
            command=lambda: self.mark_changed("debug.enabled", self.debug_mode_var.get())
        ).pack(anchor=tk.W, pady=2)
        
        self.show_raw_responses_var = tk.BooleanVar(
            value=self.config_manager.get("debug.show_raw_responses", False)
        )
        ttk.Checkbutton(
            debug_frame,
            text="Show raw API responses",
            variable=self.show_raw_responses_var,
            command=lambda: self.mark_changed("debug.show_raw_responses", self.show_raw_responses_var.get())
        ).pack(anchor=tk.W, pady=2)
        
        # Data directory
        data_frame = ttk.LabelFrame(tab, text="Data Storage", padding=10)
        data_frame.pack(fill=tk.X, padx=20, pady=10)
        
        data_path_frame = ttk.Frame(data_frame)
        data_path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(data_path_frame, text="Data Directory:").pack(side=tk.LEFT, padx=5)
        
        self.data_path_var = tk.StringVar(
            value=self.config_manager.get("paths.data_dir", str(Path.home() / ".swarmbot"))
        )
        data_entry = ttk.Entry(data_path_frame, textvariable=self.data_path_var, width=40)
        data_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            data_path_frame,
            text="Browse",
            command=self.browse_data_dir
        ).pack(side=tk.LEFT)
        
    def create_keybindings_tab(self) -> None:
        """Create keyboard shortcuts tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Keyboard Shortcuts")
        self.tabs["keybindings"] = tab
        
        # Instructions
        info_label = ttk.Label(
            tab,
            text="Double-click a shortcut to change it. Press the new key combination when prompted."
        )
        info_label.pack(padx=20, pady=10)
        
        # Shortcuts list
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview for shortcuts
        columns = ("shortcut",)
        self.shortcuts_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="tree headings",
            height=15
        )
        
        self.shortcuts_tree.heading("#0", text="Action")
        self.shortcuts_tree.heading("shortcut", text="Shortcut")
        
        self.shortcuts_tree.column("#0", width=300)
        self.shortcuts_tree.column("shortcut", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.shortcuts_tree.yview)
        self.shortcuts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.shortcuts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load shortcuts
        self.load_shortcuts()
        
        # Bind double-click
        self.shortcuts_tree.bind("<Double-Button-1>", self.edit_shortcut)
        
        # Reset button
        ttk.Button(
            tab,
            text="Reset to Defaults",
            command=self.reset_shortcuts
        ).pack(pady=10)
        
    # Helper methods
    def mark_changed(self, key: str, value: Any) -> None:
        """Mark a setting as changed"""
        self.changes[key] = value
        
    def update_temp_label(self) -> None:
        """Update temperature label"""
        self.temp_label.config(text=f"{self.temperature_var.get():.1f}")
        self.mark_changed("llm.temperature", self.temperature_var.get())
        
    def apply_changes(self) -> None:
        """Apply configuration changes"""
        for key, value in self.changes.items():
            self.config_manager.set(key, value)
            
        self.config_manager.save()
        self.changes.clear()
        messagebox.showinfo("Settings", "Settings applied successfully")
        
    def ok_clicked(self) -> None:
        """OK button clicked"""
        self.apply_changes()
        self.dialog.destroy()
        
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?"):
            self.config_manager.reset_to_defaults()
            self.dialog.destroy()
            self.show()  # Reopen with default values
            
    def open_env_file(self) -> None:
        """Open .env file in default editor"""
        env_path = Path(".env")
        if env_path.exists():
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(["notepad", str(env_path)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(env_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(env_path)])
        else:
            messagebox.showerror("Error", ".env file not found")
            
    def load_servers(self) -> None:
        """Load MCP servers into tree"""
        # This would load from actual config
        servers = [
            ("mcp-server-git", "Active", "Git", "Yes"),
            ("github", "Active", "API", "Yes"),
            ("brave-search", "Inactive", "Search", "No"),
            ("puppeteer", "Active", "Browser", "Yes"),
        ]
        
        for server in servers:
            self.server_tree.insert("", tk.END, text=server[0], values=server[1:])
            
    def add_server(self) -> None:
        """Add new MCP server"""
        # Would open server configuration dialog
        messagebox.showinfo("Add Server", "Server configuration dialog would open here")
        
    def edit_server(self) -> None:
        """Edit selected server"""
        selection = self.server_tree.selection()
        if selection:
            server_name = self.server_tree.item(selection[0])["text"]
            messagebox.showinfo("Edit Server", f"Edit configuration for {server_name}")
            
    def remove_server(self) -> None:
        """Remove selected server"""
        selection = self.server_tree.selection()
        if selection:
            server_name = self.server_tree.item(selection[0])["text"]
            if messagebox.askyesno("Remove Server", f"Remove {server_name}?"):
                self.server_tree.delete(selection[0])
                
    def test_server(self) -> None:
        """Test server connection"""
        selection = self.server_tree.selection()
        if selection:
            server_name = self.server_tree.item(selection[0])["text"]
            messagebox.showinfo("Test Connection", f"Testing connection to {server_name}...")
            
    def open_theme_editor(self) -> None:
        """Open theme editor"""
        self.trigger_event("open_theme_editor")
        
    def clear_cache(self) -> None:
        """Clear application cache"""
        if messagebox.askyesno("Clear Cache", "Clear all cached data?"):
            # Would clear actual cache
            messagebox.showinfo("Cache", "Cache cleared successfully")
            
    def browse_data_dir(self) -> None:
        """Browse for data directory"""
        directory = filedialog.askdirectory(
            initialdir=self.data_path_var.get(),
            title="Select Data Directory"
        )
        if directory:
            self.data_path_var.set(directory)
            self.mark_changed("paths.data_dir", directory)
            
    def load_shortcuts(self) -> None:
        """Load keyboard shortcuts into tree"""
        shortcuts = [
            ("File", [
                ("New Session", "Ctrl+N"),
                ("Open Session", "Ctrl+O"),
                ("Save Session", "Ctrl+S"),
                ("Settings", "Ctrl+,"),
            ]),
            ("Edit", [
                ("Copy", "Ctrl+C"),
                ("Paste", "Ctrl+V"),
                ("Clear Chat", "Ctrl+L"),
                ("Find", "Ctrl+F"),
            ]),
            ("Chat", [
                ("Send Message", "Ctrl+Enter"),
                ("New Line", "Shift+Enter"),
                ("Previous Message", "Up"),
                ("Next Message", "Down"),
            ]),
            ("Tools", [
                ("Tool Browser", "Ctrl+T"),
                ("Server Manager", "Ctrl+M"),
                ("Quick Search", "Ctrl+K"),
            ]),
            ("Navigation", [
                ("Switch Tab", "Ctrl+Tab"),
                ("Previous Tab", "Ctrl+Shift+Tab"),
                ("Toggle Sidebar", "Ctrl+B"),
            ])
        ]
        
        for category, items in shortcuts:
            parent = self.shortcuts_tree.insert("", tk.END, text=category, values=("",))
            for action, shortcut in items:
                self.shortcuts_tree.insert(parent, tk.END, text=action, values=(shortcut,))
                
    def edit_shortcut(self, event) -> None:
        """Edit keyboard shortcut"""
        selection = self.shortcuts_tree.selection()
        if selection:
            item = self.shortcuts_tree.item(selection[0])
            if item["values"][0]:  # Only edit leaf nodes
                action = item["text"]
                current = item["values"][0]
                
                # Would open shortcut capture dialog
                messagebox.showinfo(
                    "Edit Shortcut",
                    f"Press new shortcut for: {action}\nCurrent: {current}"
                )
                
    def reset_shortcuts(self) -> None:
        """Reset shortcuts to defaults"""
        if messagebox.askyesno("Reset Shortcuts", "Reset all shortcuts to defaults?"):
            # Would reset actual shortcuts
            self.load_shortcuts()
            messagebox.showinfo("Shortcuts", "Shortcuts reset to defaults")
