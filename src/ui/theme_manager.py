"""
Theme Manager for SwarmBot UI
Provides customizable themes and color schemes
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class Theme:
    """Theme configuration"""
    name: str
    colors: Dict[str, str]
    fonts: Dict[str, tuple]
    styles: Dict[str, Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary"""
        return {
            "name": self.name,
            "colors": self.colors,
            "fonts": self.fonts,
            "styles": self.styles
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Theme':
        """Create theme from dictionary"""
        return cls(
            name=data["name"],
            colors=data["colors"],
            fonts=data["fonts"],
            styles=data["styles"]
        )


class ThemeManager:
    """Manages UI themes and styling"""
    
    # Built-in themes
    DARK_THEME = Theme(
        name="Dark",
        colors={
            "bg": "#1e1e1e",
            "fg": "#ffffff",
            "select_bg": "#3d3d3d",
            "select_fg": "#ffffff",
            "button_bg": "#2d2d2d",
            "button_fg": "#ffffff",
            "entry_bg": "#2d2d2d",
            "entry_fg": "#ffffff",
            "highlight": "#007acc",
            "error": "#f44336",
            "warning": "#ff9800",
            "success": "#4caf50",
            "info": "#2196f3",
            "border": "#3d3d3d",
            "scrollbar": "#3d3d3d",
            "menu_bg": "#252525",
            "tooltip_bg": "#3d3d3d",
            "tooltip_fg": "#ffffff"
        },
        fonts={
            "default": ("Segoe UI", 10),
            "heading": ("Segoe UI", 12, "bold"),
            "small": ("Segoe UI", 9),
            "mono": ("Consolas", 10),
            "chat": ("Segoe UI", 11)
        },
        styles={
            "TLabel": {"background": "#1e1e1e", "foreground": "#ffffff"},
            "TButton": {
                "background": "#2d2d2d",
                "foreground": "#ffffff",
                "borderwidth": 0,
                "focuscolor": "none",
                "lightcolor": "#3d3d3d",
                "darkcolor": "#1e1e1e"
            },
            "TEntry": {
                "fieldbackground": "#2d2d2d",
                "foreground": "#ffffff",
                "insertcolor": "#ffffff",
                "borderwidth": 1
            },
            "TFrame": {"background": "#1e1e1e", "borderwidth": 0},
            "TPanedwindow": {"background": "#1e1e1e"},
            "TNotebook": {"background": "#1e1e1e", "borderwidth": 0},
            "TNotebook.Tab": {
                "background": "#2d2d2d",
                "foreground": "#ffffff",
                "padding": [20, 10]
            },
            "Treeview": {
                "background": "#2d2d2d",
                "foreground": "#ffffff",
                "fieldbackground": "#2d2d2d",
                "borderwidth": 0
            },
            "TScrollbar": {
                "background": "#3d3d3d",
                "borderwidth": 0,
                "arrowcolor": "#ffffff",
                "troughcolor": "#1e1e1e"
            },
            "TProgressbar": {
                "background": "#007acc",
                "troughcolor": "#2d2d2d",
                "borderwidth": 0
            }
        }
    )
    
    LIGHT_THEME = Theme(
        name="Light",
        colors={
            "bg": "#ffffff",
            "fg": "#000000",
            "select_bg": "#e0e0e0",
            "select_fg": "#000000",
            "button_bg": "#f0f0f0",
            "button_fg": "#000000",
            "entry_bg": "#ffffff",
            "entry_fg": "#000000",
            "highlight": "#2196f3",
            "error": "#d32f2f",
            "warning": "#f57c00",
            "success": "#388e3c",
            "info": "#1976d2",
            "border": "#e0e0e0",
            "scrollbar": "#cccccc",
            "menu_bg": "#f5f5f5",
            "tooltip_bg": "#333333",
            "tooltip_fg": "#ffffff"
        },
        fonts={
            "default": ("Segoe UI", 10),
            "heading": ("Segoe UI", 12, "bold"),
            "small": ("Segoe UI", 9),
            "mono": ("Consolas", 10),
            "chat": ("Segoe UI", 11)
        },
        styles={
            "TLabel": {"background": "#ffffff", "foreground": "#000000"},
            "TButton": {
                "background": "#f0f0f0",
                "foreground": "#000000",
                "borderwidth": 1,
                "relief": "raised"
            },
            "TEntry": {
                "fieldbackground": "#ffffff",
                "foreground": "#000000",
                "insertcolor": "#000000",
                "borderwidth": 1
            },
            "TFrame": {"background": "#ffffff", "borderwidth": 0},
            "TPanedwindow": {"background": "#ffffff"},
            "TNotebook": {"background": "#ffffff"},
            "TNotebook.Tab": {
                "background": "#f0f0f0",
                "foreground": "#000000",
                "padding": [20, 10]
            },
            "Treeview": {
                "background": "#ffffff",
                "foreground": "#000000",
                "fieldbackground": "#ffffff"
            },
            "TScrollbar": {
                "background": "#cccccc",
                "borderwidth": 0,
                "arrowcolor": "#666666",
                "troughcolor": "#f0f0f0"
            },
            "TProgressbar": {
                "background": "#2196f3",
                "troughcolor": "#e0e0e0",
                "borderwidth": 0
            }
        }
    )
    
    NORD_THEME = Theme(
        name="Nord",
        colors={
            "bg": "#2e3440",
            "fg": "#eceff4",
            "select_bg": "#4c566a",
            "select_fg": "#eceff4",
            "button_bg": "#3b4252",
            "button_fg": "#eceff4",
            "entry_bg": "#3b4252",
            "entry_fg": "#eceff4",
            "highlight": "#88c0d0",
            "error": "#bf616a",
            "warning": "#d08770",
            "success": "#a3be8c",
            "info": "#5e81ac",
            "border": "#4c566a",
            "scrollbar": "#4c566a",
            "menu_bg": "#3b4252",
            "tooltip_bg": "#434c5e",
            "tooltip_fg": "#eceff4"
        },
        fonts={
            "default": ("Segoe UI", 10),
            "heading": ("Segoe UI", 12, "bold"),
            "small": ("Segoe UI", 9),
            "mono": ("Consolas", 10),
            "chat": ("Segoe UI", 11)
        },
        styles={
            "TLabel": {"background": "#2e3440", "foreground": "#eceff4"},
            "TButton": {
                "background": "#3b4252",
                "foreground": "#eceff4",
                "borderwidth": 0,
                "focuscolor": "none"
            },
            "TEntry": {
                "fieldbackground": "#3b4252",
                "foreground": "#eceff4",
                "insertcolor": "#eceff4",
                "borderwidth": 0
            },
            "TFrame": {"background": "#2e3440", "borderwidth": 0},
            "TPanedwindow": {"background": "#2e3440"},
            "TNotebook": {"background": "#2e3440", "borderwidth": 0},
            "TNotebook.Tab": {
                "background": "#3b4252",
                "foreground": "#eceff4",
                "padding": [20, 10]
            },
            "Treeview": {
                "background": "#3b4252",
                "foreground": "#eceff4",
                "fieldbackground": "#3b4252",
                "borderwidth": 0
            },
            "TScrollbar": {
                "background": "#4c566a",
                "borderwidth": 0,
                "arrowcolor": "#eceff4",
                "troughcolor": "#2e3440"
            },
            "TProgressbar": {
                "background": "#88c0d0",
                "troughcolor": "#3b4252",
                "borderwidth": 0
            }
        }
    )
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.style = ttk.Style()
        self.themes: Dict[str, Theme] = {
            "Dark": self.DARK_THEME,
            "Light": self.LIGHT_THEME,
            "Nord": self.NORD_THEME
        }
        self.current_theme_name = "Dark"
        self.theme_file = Path.home() / ".swarmbot" / "themes.json"
        self.load_custom_themes()
        
    def load_custom_themes(self) -> None:
        """Load custom themes from file"""
        if self.theme_file.exists():
            try:
                with open(self.theme_file, 'r') as f:
                    custom_themes = json.load(f)
                    for theme_data in custom_themes:
                        theme = Theme.from_dict(theme_data)
                        self.themes[theme.name] = theme
            except Exception as e:
                logger.error(f"Error loading custom themes: {e}")
                
    def save_custom_themes(self) -> None:
        """Save custom themes to file"""
        try:
            custom_themes = []
            for name, theme in self.themes.items():
                if name not in ["Dark", "Light", "Nord"]:  # Skip built-in themes
                    custom_themes.append(theme.to_dict())
            
            self.theme_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.theme_file, 'w') as f:
                json.dump(custom_themes, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving custom themes: {e}")
            
    def apply_theme(self, theme_name: str) -> None:
        """Apply a theme to the application"""
        if theme_name not in self.themes:
            logger.error(f"Theme {theme_name} not found")
            return
            
        theme = self.themes[theme_name]
        self.current_theme_name = theme_name
        
        # Configure ttk styles
        for style_name, style_config in theme.styles.items():
            self.style.configure(style_name, **style_config)
            
        # Configure root window
        self.root.configure(bg=theme.colors["bg"])
        
        # Configure option database for tk widgets
        self.root.option_add('*background', theme.colors["bg"])
        self.root.option_add('*foreground', theme.colors["fg"])
        self.root.option_add('*selectBackground', theme.colors["select_bg"])
        self.root.option_add('*selectForeground', theme.colors["select_fg"])
        self.root.option_add('*Entry.background', theme.colors["entry_bg"])
        self.root.option_add('*Entry.foreground', theme.colors["entry_fg"])
        self.root.option_add('*Button.background', theme.colors["button_bg"])
        self.root.option_add('*Button.foreground', theme.colors["button_fg"])
        
        # Update all widgets
        self.update_widget_colors(self.root, theme)
        
    def update_widget_colors(self, widget, theme: Theme) -> None:
        """Recursively update widget colors"""
        try:
            # Update widget colors based on its type
            if isinstance(widget, tk.Text):
                widget.configure(
                    bg=theme.colors["entry_bg"],
                    fg=theme.colors["entry_fg"],
                    insertbackground=theme.colors["entry_fg"],
                    selectbackground=theme.colors["select_bg"],
                    selectforeground=theme.colors["select_fg"]
                )
            elif isinstance(widget, tk.Entry):
                widget.configure(
                    bg=theme.colors["entry_bg"],
                    fg=theme.colors["entry_fg"],
                    insertbackground=theme.colors["entry_fg"],
                    selectbackground=theme.colors["select_bg"],
                    selectforeground=theme.colors["select_fg"]
                )
            elif isinstance(widget, tk.Listbox):
                widget.configure(
                    bg=theme.colors["entry_bg"],
                    fg=theme.colors["entry_fg"],
                    selectbackground=theme.colors["select_bg"],
                    selectforeground=theme.colors["select_fg"]
                )
            elif isinstance(widget, tk.Button):
                widget.configure(
                    bg=theme.colors["button_bg"],
                    fg=theme.colors["button_fg"],
                    activebackground=theme.colors["select_bg"],
                    activeforeground=theme.colors["select_fg"]
                )
            elif isinstance(widget, tk.Label):
                widget.configure(
                    bg=theme.colors["bg"],
                    fg=theme.colors["fg"]
                )
            elif isinstance(widget, tk.Frame) or isinstance(widget, tk.Toplevel):
                widget.configure(bg=theme.colors["bg"])
                
            # Recursively update children
            for child in widget.winfo_children():
                self.update_widget_colors(child, theme)
                
        except tk.TclError:
            # Some widgets might not support all color options
            pass
            
    def get_current_theme(self) -> Theme:
        """Get the current theme"""
        return self.themes[self.current_theme_name]
        
    def get_color(self, color_name: str) -> str:
        """Get a color from the current theme"""
        return self.get_current_theme().colors.get(color_name, "#ffffff")
        
    def get_font(self, font_name: str) -> tuple:
        """Get a font from the current theme"""
        return self.get_current_theme().fonts.get(font_name, ("Segoe UI", 10))
        
    def show_selector(self) -> None:
        """Show theme selection dialog"""
        dialog = ThemeSelectorDialog(self.root, self)
        dialog.show()
        
    def create_custom_theme(self, base_theme: str = "Dark") -> Optional[Theme]:
        """Create a custom theme based on an existing theme"""
        dialog = ThemeEditorDialog(self.root, self, base_theme)
        return dialog.show()
        
    def delete_theme(self, theme_name: str) -> bool:
        """Delete a custom theme"""
        if theme_name in ["Dark", "Light", "Nord"]:
            messagebox.showerror("Error", "Cannot delete built-in themes")
            return False
            
        if theme_name in self.themes:
            del self.themes[theme_name]
            self.save_custom_themes()
            return True
        return False


class ThemeSelectorDialog:
    """Theme selection dialog"""
    
    def __init__(self, parent: tk.Widget, theme_manager: ThemeManager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.dialog = None
        self.selected_theme = None
        
    def show(self) -> None:
        """Show the dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Theme")
        self.dialog.geometry("400x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Theme list
        list_frame = ttk.Frame(self.dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.theme_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            font=("Segoe UI", 11)
        )
        self.theme_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.theme_listbox.yview)
        
        # Populate theme list
        for theme_name in sorted(self.theme_manager.themes.keys()):
            self.theme_listbox.insert(tk.END, theme_name)
            
        # Select current theme
        current_index = list(self.theme_manager.themes.keys()).index(
            self.theme_manager.current_theme_name
        )
        self.theme_listbox.selection_set(current_index)
        self.theme_listbox.bind("<<ListboxSelect>>", self.on_theme_select)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(self.dialog, text="Preview", padding=10)
        preview_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.preview_label = ttk.Label(preview_frame, text="Sample Text")
        self.preview_label.pack()
        
        self.preview_button = ttk.Button(preview_frame, text="Sample Button")
        self.preview_button.pack(pady=5)
        
        self.preview_entry = ttk.Entry(preview_frame)
        self.preview_entry.insert(0, "Sample Input")
        self.preview_entry.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="Apply",
            command=self.apply_theme
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame,
            text="New Theme",
            command=self.create_theme
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame,
            text="Edit",
            command=self.edit_theme
        ).pack(side=tk.LEFT, padx=5)
        
    def on_theme_select(self, event) -> None:
        """Handle theme selection"""
        selection = self.theme_listbox.curselection()
        if selection:
            theme_name = self.theme_listbox.get(selection[0])
            self.preview_theme(theme_name)
            
    def preview_theme(self, theme_name: str) -> None:
        """Preview selected theme"""
        # This would show a preview of the theme
        pass
        
    def apply_theme(self) -> None:
        """Apply selected theme"""
        selection = self.theme_listbox.curselection()
        if selection:
            theme_name = self.theme_listbox.get(selection[0])
            self.theme_manager.apply_theme(theme_name)
            self.dialog.destroy()
            
    def create_theme(self) -> None:
        """Create a new theme"""
        theme = self.theme_manager.create_custom_theme()
        if theme:
            self.theme_listbox.insert(tk.END, theme.name)
            
    def edit_theme(self) -> None:
        """Edit selected theme"""
        selection = self.theme_listbox.curselection()
        if selection:
            theme_name = self.theme_listbox.get(selection[0])
            if theme_name in ["Dark", "Light", "Nord"]:
                messagebox.showinfo("Info", "Built-in themes cannot be edited")
            else:
                # Open theme editor
                pass


class ThemeEditorDialog:
    """Theme editor dialog"""
    
    def __init__(self, parent: tk.Widget, theme_manager: ThemeManager, base_theme: str):
        self.parent = parent
        self.theme_manager = theme_manager
        self.base_theme = base_theme
        self.dialog = None
        self.new_theme = None
        self.color_entries = {}
        
    def show(self) -> Optional[Theme]:
        """Show the dialog and return created theme"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Create Custom Theme")
        self.dialog.geometry("500x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create a copy of the base theme
        base = self.theme_manager.themes[self.base_theme]
        self.new_theme = Theme(
            name="Custom Theme",
            colors=base.colors.copy(),
            fonts=base.fonts.copy(),
            styles=base.styles.copy()
        )
        
        # Name entry
        name_frame = ttk.Frame(self.dialog)
        name_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(name_frame, text="Theme Name:").pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(name_frame)
        self.name_entry.insert(0, "Custom Theme")
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Color editor
        color_frame = ttk.LabelFrame(self.dialog, text="Colors", padding=10)
        color_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create scrollable frame for colors
        canvas = tk.Canvas(color_frame)
        scrollbar = ttk.Scrollbar(color_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add color entries
        for i, (color_name, color_value) in enumerate(self.new_theme.colors.items()):
            row_frame = ttk.Frame(scrollable_frame)
            row_frame.grid(row=i, column=0, sticky="ew", pady=2)
            
            ttk.Label(row_frame, text=color_name.replace("_", " ").title()).pack(side=tk.LEFT, padx=5)
            
            color_label = tk.Label(
                row_frame,
                text="    ",
                bg=color_value,
                relief=tk.RAISED,
                bd=1
            )
            color_label.pack(side=tk.RIGHT, padx=5)
            
            entry = ttk.Entry(row_frame, width=10)
            entry.insert(0, color_value)
            entry.pack(side=tk.RIGHT, padx=5)
            
            self.color_entries[color_name] = (entry, color_label)
            
            # Color picker button
            ttk.Button(
                row_frame,
                text="...",
                width=3,
                command=lambda cn=color_name: self.pick_color(cn)
            ).pack(side=tk.RIGHT)
            
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="Create",
            command=self.create_theme
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
        
        self.dialog.wait_window()
        return self.new_theme if hasattr(self, 'created') else None
        
    def pick_color(self, color_name: str) -> None:
        """Open color picker for a color"""
        entry, label = self.color_entries[color_name]
        initial_color = entry.get()
        
        color = colorchooser.askcolor(initialcolor=initial_color, parent=self.dialog)
        if color[1]:  # If a color was chosen
            entry.delete(0, tk.END)
            entry.insert(0, color[1])
            label.configure(bg=color[1])
            
    def create_theme(self) -> None:
        """Create the theme"""
        # Update theme with new values
        self.new_theme.name = self.name_entry.get()
        
        for color_name, (entry, _) in self.color_entries.items():
            self.new_theme.colors[color_name] = entry.get()
            
        # Add to theme manager
        self.theme_manager.themes[self.new_theme.name] = self.new_theme
        self.theme_manager.save_custom_themes()
        
        self.created = True
        self.dialog.destroy()
