"""
Error Display UI Component
Shows error messages and stack traces
"""

from .base import UIComponent
import tkinter as tk
from tkinter import ttk, scrolledtext
import traceback


class ErrorDisplay(UIComponent):
    """Error display dialog for showing error messages"""
    
    def __init__(self, parent=None):
        """Initialize error display"""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the error display UI"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Error")
        self.window.geometry("600x400")
        
        # Create main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Error icon and message frame
        msg_frame = ttk.Frame(main_frame)
        msg_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Error icon (using text for simplicity)
        icon_label = ttk.Label(msg_frame, text="⚠", font=('Arial', 24), foreground='red')
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Error message
        self.message_label = ttk.Label(
            msg_frame,
            text="An error occurred",
            font=('Arial', 11, 'bold'),
            wraplength=500
        )
        self.message_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Error Details", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Error details text
        self.details_text = scrolledtext.ScrolledText(
            details_frame,
            wrap=tk.WORD,
            width=60,
            height=15,
            font=('Consolas', 9)
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Copy button
        self.copy_button = ttk.Button(
            button_frame,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard
        )
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        self.close_button = ttk.Button(
            button_frame,
            text="Close",
            command=self.hide
        )
        self.close_button.pack(side=tk.RIGHT)
        
        # Initially hide
        self.window.withdraw()
        
        # Bind Escape key to close
        self.window.bind('<Escape>', lambda e: self.hide())
    
    def show_error(self, title="Error", message="An error occurred", details=None, exception=None):
        """Show an error
        
        Args:
            title: Window title
            message: Main error message
            details: Optional error details
            exception: Optional exception object
        """
        self.window.title(title)
        self.message_label.config(text=message)
        
        # Clear details
        self.details_text.delete(1.0, tk.END)
        
        # Add details
        if exception:
            # Format exception with traceback
            tb_str = ''.join(traceback.format_exception(
                type(exception),
                exception,
                exception.__traceback__
            ))
            self.details_text.insert(1.0, tb_str)
        elif details:
            self.details_text.insert(1.0, details)
        else:
            self.details_text.insert(1.0, message)
        
        # Show window
        self.window.deiconify()
        self.window.lift()
        self.window.grab_set()  # Make modal
        
        # Center the window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def copy_to_clipboard(self):
        """Copy error details to clipboard"""
        details = self.details_text.get(1.0, tk.END).strip()
        self.window.clipboard_clear()
        self.window.clipboard_append(details)
        
        # Temporarily change button text
        original_text = self.copy_button['text']
        self.copy_button.config(text="Copied!")
        self.window.after(1500, lambda: self.copy_button.config(text=original_text))
    
    def hide(self):
        """Hide the error display"""
        self.window.grab_release()
        self.window.withdraw()
    
    def destroy(self):
        """Destroy the error window"""
        self.window.destroy()
