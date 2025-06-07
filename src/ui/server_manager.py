"""
Server Manager Panel for SwarmBot UI
Manages MCP server connections and status
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import logging
from .base import UIComponent

logger = logging.getLogger(__name__)


class ServerManagerPanel(UIComponent):
    """Panel for managing MCP server connections"""
    
    def __init__(self, parent: tk.Widget, server_manager: Any, **kwargs):
        super().__init__(parent, **kwargs)
        self.server_manager = server_manager
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.selected_server = None
        
    def build(self) -> None:
        """Build the server manager panel"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Label(header_frame, text="MCP Servers", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        
        # Action buttons
        self.refresh_btn = ttk.Button(
            header_frame,
            text="🔄",
            width=3,
            command=self.refresh_servers
        )
        self.refresh_btn.pack(side=tk.RIGHT, padx=2)
        
        self.connect_all_btn = ttk.Button(
            header_frame,
            text="Connect All",
            command=self.connect_all_servers
        )
        self.connect_all_btn.pack(side=tk.RIGHT, padx=2)
        
        # Server list
        self.create_server_list()
        
        # Details panel
        self.create_details_panel()
        
        # Initial load
        self.refresh_servers()
        
    def create_server_list(self) -> None:
        """Create the server list view"""
        # List frame
        list_frame = ttk.Frame(self.frame)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ("status", "type", "tools")
        self.server_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="tree headings",
            selectmode="browse",
            height=10
        )
        
        # Configure columns
        self.server_tree.heading("#0", text="Server")
        self.server_tree.heading("status", text="Status")
        self.server_tree.heading("type", text="Type")
        self.server_tree.heading("tools", text="Tools")
        
        self.server_tree.column("#0", width=150)
        self.server_tree.column("status", width=80)
        self.server_tree.column("type", width=60)
        self.server_tree.column("tools", width=50)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.server_tree.yview)
        self.server_tree.configure(yscrollcommand=scrollbar.set)
        
        self.server_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind events
        self.server_tree.bind("<<TreeviewSelect>>", self.on_server_select)
        self.server_tree.bind("<Double-Button-1>", self.on_server_double_click)
        
        # Context menu
        self.create_context_menu()
        self.server_tree.bind("<Button-3>", self.show_context_menu)
        
    def create_details_panel(self) -> None:
        """Create the server details panel"""
        # Details frame
        self.details_frame = ttk.LabelFrame(self.frame, text="Server Details", padding=10)
        self.details_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.details_frame.columnconfigure(1, weight=1)
        
        # Server info labels
        self.info_labels = {}
        info_fields = [
            ("Name:", "name"),
            ("Status:", "status"),
            ("Type:", "type"),
            ("Command:", "command"),
            ("Connected:", "connected_time"),
            ("Tools:", "tool_count"),
            ("Errors:", "error_count")
        ]
        
        for i, (label, field) in enumerate(info_fields):
            ttk.Label(self.details_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            info_label = ttk.Label(self.details_frame, text="-")
            info_label.grid(row=i, column=1, sticky="w", pady=2)
            self.info_labels[field] = info_label
            
        # Action buttons
        button_frame = ttk.Frame(self.details_frame)
        button_frame.grid(row=len(info_fields), column=0, columnspan=2, pady=10)
        
        self.connect_btn = ttk.Button(
            button_frame,
            text="Connect",
            command=self.toggle_connection,
            state=tk.DISABLED
        )
        self.connect_btn.pack(side=tk.LEFT, padx=2)
        
        self.restart_btn = ttk.Button(
            button_frame,
            text="Restart",
            command=self.restart_server,
            state=tk.DISABLED
        )
        self.restart_btn.pack(side=tk.LEFT, padx=2)
        
        self.view_logs_btn = ttk.Button(
            button_frame,
            text="View Logs",
            command=self.view_server_logs,
            state=tk.DISABLED
        )
        self.view_logs_btn.pack(side=tk.LEFT, padx=2)
        
        self.test_btn = ttk.Button(
            button_frame,
            text="Test",
            command=self.test_server,
            state=tk.DISABLED
        )
        self.test_btn.pack(side=tk.LEFT, padx=2)
        
    def create_context_menu(self) -> None:
        """Create context menu for server list"""
        self.context_menu = tk.Menu(self.server_tree, tearoff=0)
        self.context_menu.add_command(label="Connect", command=self.connect_server)
        self.context_menu.add_command(label="Disconnect", command=self.disconnect_server)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Restart", command=self.restart_server)
        self.context_menu.add_command(label="Test Connection", command=self.test_server)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Tools", command=self.view_server_tools)
        self.context_menu.add_command(label="View Logs", command=self.view_server_logs)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Configure", command=self.configure_server)
        
    def refresh_servers(self) -> None:
        """Refresh the server list"""
        # Clear current list
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)
            
        # Get servers from manager
        servers = self.server_manager.get_servers()
        
        for server_name, server_info in servers.items():
            # Determine status icon and text
            status = server_info.get("status", "disconnected")
            if status == "connected":
                status_icon = "🟢"
                status_text = "Connected"
            elif status == "connecting":
                status_icon = "🟡"
                status_text = "Connecting"
            elif status == "error":
                status_icon = "🔴"
                status_text = "Error"
            else:
                status_icon = "⚪"
                status_text = "Disconnected"
                
            # Get server type
            server_type = server_info.get("type", "Unknown")
            if server_info.get("command", "").startswith("npx"):
                server_type = "NPX"
            elif server_info.get("command", "").startswith("uvx"):
                server_type = "UVX"
            elif server_info.get("command", "").endswith(".py"):
                server_type = "Python"
                
            # Count tools
            tool_count = len(server_info.get("tools", []))
            
            # Insert into tree
            item = self.server_tree.insert(
                "",
                tk.END,
                text=f"{status_icon} {server_name}",
                values=(status_text, server_type, str(tool_count))
            )
            
            # Store server info
            self.servers[item] = server_info.copy()
            self.servers[item]["name"] = server_name
            
        # Update refresh button
        self.refresh_btn.config(text="🔄")
        
    def on_server_select(self, event) -> None:
        """Handle server selection"""
        selection = self.server_tree.selection()
        if selection:
            self.selected_server = selection[0]
            self.update_details_panel()
            self.enable_action_buttons()
        else:
            self.selected_server = None
            self.clear_details_panel()
            self.disable_action_buttons()
            
    def on_server_double_click(self, event) -> None:
        """Handle server double-click"""
        if self.selected_server:
            self.toggle_connection()
            
    def update_details_panel(self) -> None:
        """Update the details panel with selected server info"""
        if not self.selected_server:
            return
            
        server_info = self.servers.get(self.selected_server, {})
        
        # Update info labels
        self.info_labels["name"].config(text=server_info.get("name", "-"))
        self.info_labels["status"].config(text=server_info.get("status", "disconnected").title())
        self.info_labels["type"].config(text=server_info.get("type", "Unknown"))
        self.info_labels["command"].config(text=server_info.get("command", "-"))
        
        # Connected time
        if server_info.get("connected_time"):
            connected_time = server_info["connected_time"]
            if isinstance(connected_time, datetime):
                duration = datetime.now() - connected_time
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                time_str = str(connected_time)
        else:
            time_str = "-"
        self.info_labels["connected_time"].config(text=time_str)
        
        # Tool count
        tool_count = len(server_info.get("tools", []))
        self.info_labels["tool_count"].config(text=str(tool_count))
        
        # Error count
        error_count = server_info.get("error_count", 0)
        self.info_labels["error_count"].config(text=str(error_count))
        
        # Update button text
        if server_info.get("status") == "connected":
            self.connect_btn.config(text="Disconnect")
        else:
            self.connect_btn.config(text="Connect")
            
    def clear_details_panel(self) -> None:
        """Clear the details panel"""
        for label in self.info_labels.values():
            label.config(text="-")
            
    def enable_action_buttons(self) -> None:
        """Enable action buttons"""
        self.connect_btn.config(state=tk.NORMAL)
        self.restart_btn.config(state=tk.NORMAL)
        self.view_logs_btn.config(state=tk.NORMAL)
        self.test_btn.config(state=tk.NORMAL)
        
    def disable_action_buttons(self) -> None:
        """Disable action buttons"""
        self.connect_btn.config(state=tk.DISABLED)
        self.restart_btn.config(state=tk.DISABLED)
        self.view_logs_btn.config(state=tk.DISABLED)
        self.test_btn.config(state=tk.DISABLED)
        
    def show_context_menu(self, event) -> None:
        """Show context menu"""
        # Select item under cursor
        item = self.server_tree.identify("item", event.x, event.y)
        if item:
            self.server_tree.selection_set(item)
            self.selected_server = item
            
            # Update menu items based on server status
            server_info = self.servers.get(item, {})
            if server_info.get("status") == "connected":
                self.context_menu.entryconfig("Connect", state=tk.DISABLED)
                self.context_menu.entryconfig("Disconnect", state=tk.NORMAL)
            else:
                self.context_menu.entryconfig("Connect", state=tk.NORMAL)
                self.context_menu.entryconfig("Disconnect", state=tk.DISABLED)
                
            # Show menu
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
                
    def toggle_connection(self) -> None:
        """Toggle server connection"""
        if not self.selected_server:
            return
            
        server_info = self.servers.get(self.selected_server, {})
        server_name = server_info.get("name")
        
        if server_info.get("status") == "connected":
            self.disconnect_server()
        else:
            self.connect_server()
            
    def connect_server(self) -> None:
        """Connect to selected server"""
        if not self.selected_server:
            return
            
        server_info = self.servers.get(self.selected_server, {})
        server_name = server_info.get("name")
        
        # Update UI
        self.server_tree.set(self.selected_server, "status", "Connecting")
        self.connect_btn.config(state=tk.DISABLED)
        
        # Trigger connection
        self.trigger_event("connect_server", server_name)
        
    def disconnect_server(self) -> None:
        """Disconnect from selected server"""
        if not self.selected_server:
            return
            
        server_info = self.servers.get(self.selected_server, {})
        server_name = server_info.get("name")
        
        if messagebox.askyesno("Disconnect Server", f"Disconnect from {server_name}?"):
            # Update UI
            self.server_tree.set(self.selected_server, "status", "Disconnecting")
            self.connect_btn.config(state=tk.DISABLED)
            
            # Trigger disconnection
            self.trigger_event("disconnect_server", server_name)
            
    def connect_all_servers(self) -> None:
        """Connect to all servers"""
        if messagebox.askyesno("Connect All", "Connect to all configured servers?"):
            self.trigger_event("connect_all_servers")
            
    def restart_server(self) -> None:
        """Restart selected server"""
        if not self.selected_server:
            return
            
        server_info = self.servers.get(self.selected_server, {})
        server_name = server_info.get("name")
        
        if messagebox.askyesno("Restart Server", f"Restart {server_name}?"):
            self.trigger_event("restart_server", server_name)
            
    def test_server(self) -> None:
        """Test selected server connection"""
        if not self.selected_server:
            return
            
        server_info = self.servers.get(self.selected_server, {})
        server_name = server_info.get("name")
        
        # Show testing dialog
        self.show_test_dialog(server_name)
        
    def show_test_dialog(self, server_name: str) -> None:
        """Show server test dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Testing {server_name}")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        
        # Test results text
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        test_text = tk.Text(text_frame, wrap=tk.WORD, height=10)
        test_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=test_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        test_text.config(yscrollcommand=scrollbar.set)
        
        # Add initial message
        test_text.insert(tk.END, f"Testing connection to {server_name}...\n\n")
        
        # Progress bar
        progress = ttk.Progressbar(dialog, mode='indeterminate')
        progress.pack(fill=tk.X, padx=10, pady=5)
        progress.start(10)
        
        # Close button
        close_btn = ttk.Button(dialog, text="Close", command=dialog.destroy)
        close_btn.pack(pady=10)
        
        # Run tests
        self.trigger_event("test_server", server_name, dialog, test_text, progress)
        
    def view_server_tools(self) -> None:
        """View tools for selected server"""
        if not self.selected_server:
            return
            
        server_info = self.servers.get(self.selected_server, {})
        server_name = server_info.get("name")
        tools = server_info.get("tools", [])
        
        # Show tools dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"{server_name} Tools")
        dialog.geometry("600x400")
        dialog.transient(self.parent)
        
        # Tools list
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for tools
        columns = ("description",)
        tools_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="tree headings",
            height=15
        )
        
        tools_tree.heading("#0", text="Tool Name")
        tools_tree.heading("description", text="Description")
        
        tools_tree.column("#0", width=200)
        tools_tree.column("description", width=350)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tools_tree.yview)
        tools_tree.configure(yscrollcommand=scrollbar.set)
        
        tools_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate tools
        for tool in tools:
            tools_tree.insert(
                "",
                tk.END,
                text=tool.get("name", "Unknown"),
                values=(tool.get("description", ""),)
            )
            
        # Close button
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
        
    def view_server_logs(self) -> None:
        """View logs for selected server"""
        if not self.selected_server:
            return
            
        server_info = self.servers.get(self.selected_server, {})
        server_name = server_info.get("name")
        
        self.trigger_event("view_server_logs", server_name)
        
    def configure_server(self) -> None:
        """Configure selected server"""
        if not self.selected_server:
            return
            
        server_info = self.servers.get(self.selected_server, {})
        server_name = server_info.get("name")
        
        self.trigger_event("configure_server", server_name)
        
    def update_server_status(self, server_name: str, status: str, 
                           error: Optional[str] = None) -> None:
        """Update server status in the UI"""
        # Find server in tree
        for item in self.server_tree.get_children():
            if self.servers.get(item, {}).get("name") == server_name:
                # Update status
                self.servers[item]["status"] = status
                
                # Update tree display
                if status == "connected":
                    status_icon = "🟢"
                    status_text = "Connected"
                    self.servers[item]["connected_time"] = datetime.now()
                elif status == "connecting":
                    status_icon = "🟡"
                    status_text = "Connecting"
                elif status == "error":
                    status_icon = "🔴"
                    status_text = "Error"
                    if error:
                        self.servers[item]["last_error"] = error
                        self.servers[item]["error_count"] = \
                            self.servers[item].get("error_count", 0) + 1
                else:
                    status_icon = "⚪"
                    status_text = "Disconnected"
                    self.servers[item]["connected_time"] = None
                    
                self.server_tree.item(
                    item,
                    text=f"{status_icon} {server_name}"
                )
                self.server_tree.set(item, "status", status_text)
                
                # Update details if selected
                if item == self.selected_server:
                    self.update_details_panel()
                    
                break
                
    def update_server_tools(self, server_name: str, tools: List[Dict[str, Any]]) -> None:
        """Update server tools count"""
        # Find server in tree
        for item in self.server_tree.get_children():
            if self.servers.get(item, {}).get("name") == server_name:
                self.servers[item]["tools"] = tools
                self.server_tree.set(item, "tools", str(len(tools)))
                
                # Update details if selected
                if item == self.selected_server:
                    self.update_details_panel()
                    
                break
