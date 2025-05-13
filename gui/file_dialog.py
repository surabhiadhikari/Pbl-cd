"""
File dialog implementation for handling file operations.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

class FileDialog:
    def __init__(self, parent):
        self.parent = parent
        self.current_file = None
    
    def save_file(self, content):
        """Save content to a file."""
        if not self.current_file:
            return self.save_file_as(content)
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file: {str(e)}")
            return False
    
    def save_file_as(self, content):
        """Save content to a new file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".c",
            filetypes=[
                ("C Source Files", "*.c"),
                ("Header Files", "*.h"),
                ("All Files", "*.*")
            ],
            title="Save File As"
        )
        
        if not file_path:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.current_file = file_path
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file: {str(e)}")
            return False
    
    def load_file(self):
        """Load content from a file."""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("C Source Files", "*.c"),
                ("Header Files", "*.h"),
                ("All Files", "*.*")
            ],
            title="Open File"
        )
        
        if not file_path:
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.current_file = file_path
            return content
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load file: {str(e)}")
            return None
    
    def get_current_file_name(self):
        """Get the name of the current file."""
        if self.current_file:
            return Path(self.current_file).name
        return "Untitled" 