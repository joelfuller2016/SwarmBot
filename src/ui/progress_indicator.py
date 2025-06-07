"""
Progress Indicator UI Component
Shows progress for long-running operations
"""

from .base import UIComponent
import tkinter as tk
from tkinter import ttk


class ProgressIndicator(UIComponent):
    """Progress indicator for long-running operations"""
    
    def __init__(self, parent=None):
        """Initialize progress indicator"""
        super().__init__(parent)
        self.current_value = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the progress indicator UI"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Operation Progress")
        self.window.geometry("400x150")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create main container
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Processing...", font=('Arial', 10))
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            main_frame,
            orient="horizontal",
            length=350,
            mode="determinate"
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # Details label
        self.details_label = ttk.Label(main_frame, text="", font=('Arial', 9))
        self.details_label.pack()
        
        # Initially hide
        self.window.withdraw()
    
    def show(self, title="Processing", status="Please wait..."):
        """Show the progress indicator"""
        self.window.title(title)
        self.status_label.config(text=status)
        self.details_label.config(text="")
        self.progress_bar['value'] = 0
        self.current_value = 0
        
        self.window.deiconify()
        self.window.lift()
        self.window.grab_set()  # Make modal
        self.window.update()
    
    def update(self, value, status=None, details=None):
        """Update progress
        
        Args:
            value: Progress value (0-100)
            status: Optional status message
            details: Optional details message
        """
        self.current_value = value
        self.progress_bar['value'] = value
        
        if status:
            self.status_label.config(text=status)
        
        if details:
            self.details_label.config(text=details)
        
        self.window.update()
        
        # Auto-hide when complete
        if value >= 100:
            self.window.after(500, self.hide)
    
    def hide(self):
        """Hide the progress indicator"""
        self.window.grab_release()
        self.window.withdraw()
    
    def pulse(self):
        """Switch to indeterminate mode (pulsing)"""
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(10)
    
    def stop_pulse(self):
        """Stop pulsing and switch back to determinate mode"""
        self.progress_bar.stop()
        self.progress_bar.config(mode="determinate")
    
    def destroy(self):
        """Destroy the progress window"""
        self.window.destroy()
