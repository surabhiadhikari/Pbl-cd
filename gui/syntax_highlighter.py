"""
Syntax highlighting implementation for C code.
"""

import tkinter as tk
from tkinter import font
import re

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.tag_names = {
            'keyword': 'keyword',
            'type': 'type',
            'string': 'string',
            'comment': 'comment',
            'number': 'number',
            'operator': 'operator',
            'preprocessor': 'preprocessor'
        }
        
        # Configure tags
        self._configure_tags()
        
        # Define patterns
        self.patterns = {
            'keyword': r'\b(int|char|float|double|void|if|else|while|for|do|switch|case|break|continue|return|struct|union|enum|typedef|static|extern|const|volatile|register|auto|signed|unsigned|long|short|goto|sizeof)\b',
            'type': r'\b(int|char|float|double|void|struct|union|enum|typedef)\b',
            'string': r'"[^"\\]*(\\.[^"\\]*)*"',
            'comment': r'//.*$|/\*[\s\S]*?\*/',
            'number': r'\b\d+(\.\d+)?([eE][+-]?\d+)?\b',
            'operator': r'[+\-*/%=<>!&|^~?:]',
            'preprocessor': r'^#\s*\w+'
        }
        
        # Bind events
        self.text_widget.bind('<KeyRelease>', self._on_key_release)
    
    def _configure_tags(self):
        """Configure syntax highlighting tags."""
        # Configure tag colors
        self.text_widget.tag_configure('keyword', foreground='#0000FF')
        self.text_widget.tag_configure('type', foreground='#0000FF')
        self.text_widget.tag_configure('string', foreground='#008000')
        self.text_widget.tag_configure('comment', foreground='#808080')
        self.text_widget.tag_configure('number', foreground='#FF0000')
        self.text_widget.tag_configure('operator', foreground='#000000')
        self.text_widget.tag_configure('preprocessor', foreground='#800080')
    
    def _on_key_release(self, event):
        """Handle key release events for syntax highlighting."""
        self.highlight()
    
    def highlight(self):
        """Apply syntax highlighting to the entire text."""
        # Remove existing tags
        for tag in self.tag_names.values():
            self.text_widget.tag_remove(tag, '1.0', tk.END)
        
        # Get text content
        content = self.text_widget.get('1.0', tk.END)
        
        # Apply highlighting for each pattern
        for tag_name, pattern in self.patterns.items():
            self._highlight_pattern(pattern, self.tag_names[tag_name])
    
    def _highlight_pattern(self, pattern, tag):
        """Highlight a specific pattern in the text."""
        start_index = '1.0'
        while True:
            # Search for the pattern
            start_index = self.text_widget.search(
                pattern,
                start_index,
                tk.END,
                regexp=True
            )
            
            if not start_index:
                break
            
            # Calculate end index
            end_index = self.text_widget.index(f"{start_index} + 1c")
            
            # Apply tag
            self.text_widget.tag_add(tag, start_index, end_index)
            
            # Move start index for next search
            start_index = end_index 