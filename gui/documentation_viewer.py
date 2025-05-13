"""
Documentation viewer for displaying help and documentation.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
from pathlib import Path

class DocumentationViewer:
    def __init__(self, parent):
        self.parent = parent
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Documentation")
        self.dialog.geometry("800x600")
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create main container
        self.main_container = ttk.PanedWindow(self.dialog, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel for navigation
        self.nav_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.nav_panel, weight=1)
        
        # Create right panel for content
        self.content_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.content_panel, weight=3)
        
        # Create navigation tree
        self._create_navigation()
        
        # Create content display
        self._create_content_display()
        
        # Load documentation
        self._load_documentation()
        
        # Center dialog on parent window
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_navigation(self):
        """Create the navigation tree."""
        # Create treeview
        self.nav_tree = ttk.Treeview(self.nav_panel, show="tree")
        self.nav_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.nav_panel, orient=tk.VERTICAL, command=self.nav_tree.yview)
        self.nav_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.nav_tree.bind('<<TreeviewSelect>>', self._on_nav_select)
    
    def _create_content_display(self):
        """Create the content display area."""
        # Create text widget with scrollbar
        self.content_text = tk.Text(
            self.content_panel,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            padx=10,
            pady=10
        )
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.content_panel, orient=tk.VERTICAL, command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure tags
        self.content_text.tag_configure('heading', font=("Segoe UI", 12, "bold"))
        self.content_text.tag_configure('subheading', font=("Segoe UI", 11, "bold"))
        self.content_text.tag_configure('code', font=("Consolas", 10))
        self.content_text.tag_configure('link', foreground="blue", underline=1)
        
        # Bind link click event
        self.content_text.tag_bind('link', '<Button-1>', self._on_link_click)
    
    def _load_documentation(self):
        """Load documentation content."""
        # Add main sections
        self.nav_tree.insert("", "end", "getting_started", text="Getting Started")
        self.nav_tree.insert("", "end", "features", text="Features")
        self.nav_tree.insert("", "end", "usage", text="Usage Guide")
        self.nav_tree.insert("", "end", "troubleshooting", text="Troubleshooting")
        
        # Add subsections
        self.nav_tree.insert("getting_started", "end", "installation", text="Installation")
        self.nav_tree.insert("getting_started", "end", "quick_start", text="Quick Start")
        
        self.nav_tree.insert("features", "end", "lexical_analysis", text="Lexical Analysis")
        self.nav_tree.insert("features", "end", "syntax_analysis", text="Syntax Analysis")
        self.nav_tree.insert("features", "end", "semantic_analysis", text="Semantic Analysis")
        self.nav_tree.insert("features", "end", "error_recovery", text="Error Recovery")
        
        self.nav_tree.insert("usage", "end", "editor", text="Code Editor")
        self.nav_tree.insert("usage", "end", "analysis", text="Code Analysis")
        self.nav_tree.insert("usage", "end", "settings", text="Settings")
        
        self.nav_tree.insert("troubleshooting", "end", "common_issues", text="Common Issues")
        self.nav_tree.insert("troubleshooting", "end", "faq", text="FAQ")
        
        # Expand main sections
        for section in ["getting_started", "features", "usage", "troubleshooting"]:
            self.nav_tree.item(section, open=True)
    
    def _on_nav_select(self, event):
        """Handle navigation tree selection."""
        selection = self.nav_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        self._display_content(item_id)
    
    def _display_content(self, item_id):
        """Display content for the selected item."""
        # Clear current content
        self.content_text.delete("1.0", tk.END)
        
        # Get content based on item ID
        content = self._get_content(item_id)
        
        # Insert content with appropriate tags
        for block in content:
            if block['type'] == 'heading':
                self.content_text.insert(tk.END, block['text'] + "\n\n", 'heading')
            elif block['type'] == 'subheading':
                self.content_text.insert(tk.END, block['text'] + "\n\n", 'subheading')
            elif block['type'] == 'paragraph':
                self.content_text.insert(tk.END, block['text'] + "\n\n")
            elif block['type'] == 'code':
                self.content_text.insert(tk.END, block['text'] + "\n\n", 'code')
            elif block['type'] == 'link':
                self.content_text.insert(tk.END, block['text'] + "\n\n", 'link')
    
    def _get_content(self, item_id):
        """Get content for a specific item."""
        # This is a simplified version. In a real application, content would be loaded from files
        content_map = {
            'getting_started': [
                {'type': 'heading', 'text': 'Getting Started'},
                {'type': 'paragraph', 'text': 'Welcome to the C Code Error Detection and Recovery System. This guide will help you get started with using the application.'}
            ],
            'installation': [
                {'type': 'heading', 'text': 'Installation'},
                {'type': 'paragraph', 'text': 'To install the application, follow these steps:'},
                {'type': 'code', 'text': 'pip install c-analyzer'},
                {'type': 'paragraph', 'text': 'Make sure you have Python 3.7 or later installed.'}
            ],
            'quick_start': [
                {'type': 'heading', 'text': 'Quick Start'},
                {'type': 'paragraph', 'text': 'To start using the application:'},
                {'type': 'code', 'text': 'python -m c_analyzer'},
                {'type': 'paragraph', 'text': 'This will launch the main application window.'}
            ],
            'features': [
                {'type': 'heading', 'text': 'Features'},
                {'type': 'paragraph', 'text': 'The application provides the following features:'},
                {'type': 'subheading', 'text': 'Lexical Analysis'},
                {'type': 'paragraph', 'text': 'Detects lexical errors in C code, such as invalid identifiers and malformed numbers.'},
                {'type': 'subheading', 'text': 'Syntax Analysis'},
                {'type': 'paragraph', 'text': 'Identifies syntax errors and provides suggestions for fixing them.'},
                {'type': 'subheading', 'text': 'Semantic Analysis'},
                {'type': 'paragraph', 'text': 'Checks for semantic errors like type mismatches and undefined variables.'},
                {'type': 'subheading', 'text': 'Error Recovery'},
                {'type': 'paragraph', 'text': 'Attempts to recover from errors and continue analysis.'}
            ],
            'usage': [
                {'type': 'heading', 'text': 'Usage Guide'},
                {'type': 'paragraph', 'text': 'Learn how to use the various features of the application.'}
            ],
            'troubleshooting': [
                {'type': 'heading', 'text': 'Troubleshooting'},
                {'type': 'paragraph', 'text': 'Find solutions to common problems and frequently asked questions.'}
            ]
        }
        
        return content_map.get(item_id, [{'type': 'paragraph', 'text': 'Content not available.'}])
    
    def _on_link_click(self, event):
        """Handle link clicks."""
        # Get the index of the clicked position
        index = self.content_text.index(f"@{event.x},{event.y}")
        
        # Get the link text
        link_text = self.content_text.get(index + " wordstart", index + " wordend")
        
        # Open the link in the default web browser
        webbrowser.open(link_text) 