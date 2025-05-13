"""
Main window for the C code analyzer GUI.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ..lexer.tokenizer import Tokenizer
from ..lexer.error_detection import LexicalErrorDetector
from ..parser.syntax_analyzer import SyntaxAnalyzer
from ..parser.error_recovery import ErrorRecovery
from ..semantic.type_checker import TypeChecker
from ..semantic.symbol_table import SymbolTable
from .file_dialog import FileDialog
from .syntax_highlighter import SyntaxHighlighter
from .settings_dialog import SettingsDialog
from .documentation_viewer import DocumentationViewer
import json
from pathlib import Path

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("C Code Error Detection and Recovery System")
        self.root.geometry("1200x800")
        
        # Load settings
        self.settings = self._load_settings()
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create main container
        self.main_container = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel for code editor
        self.left_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.left_panel, weight=2)
        
        # Create right panel for error display
        self.right_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.right_panel, weight=1)
        
        # Initialize file dialog
        self.file_dialog = FileDialog(root)
        
        self._create_code_editor()
        self._create_error_display()
        self._create_toolbar()
        self._create_status_bar()
        
        # Initialize analyzers
        self.tokenizer = Tokenizer("")
        self.lexical_detector = LexicalErrorDetector()
        self.syntax_analyzer = SyntaxAnalyzer()
        self.error_recovery = ErrorRecovery()
        self.type_checker = TypeChecker()
        self.symbol_table = SymbolTable()
        
        # Initialize syntax highlighter
        self.syntax_highlighter = SyntaxHighlighter(self.code_editor)
        
        # Apply initial settings
        self._apply_settings()
        
        # Update window title
        self._update_title()
        
        # Bind settings changed event
        self.root.bind('<<SettingsChanged>>', lambda e: self._apply_settings())
        
        # Bind cursor movement event
        self.code_editor.bind("<KeyRelease>", self._update_status_bar)
        self.code_editor.bind("<ButtonRelease>", self._update_status_bar)
        
        # Set up real-time analysis if enabled
        if self.settings['analysis']['real_time']:
            self._setup_real_time_analysis()
    
    def _load_settings(self):
        """Load settings from file."""
        settings_file = Path.home() / '.c_analyzer' / 'settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default settings
        return {
            'editor': {
                'font_family': 'Consolas',
                'font_size': 12,
                'tab_size': 4,
                'use_spaces': True,
                'show_line_numbers': True,
                'word_wrap': False
            },
            'theme': {
                'current': 'light',
                'colors': {
                    'keyword': '#0000FF',
                    'type': '#0000FF',
                    'string': '#008000',
                    'comment': '#808080',
                    'number': '#FF0000',
                    'operator': '#000000',
                    'preprocessor': '#800080'
                }
            },
            'analysis': {
                'real_time': False,
                'delay': 500,
                'severity': {
                    'lexical': 'error',
                    'syntax': 'error',
                    'semantic': 'error'
                }
            }
        }
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self._new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self._load_code, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self._save_code, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_code_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=lambda: self.code_editor.edit_undo(), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=lambda: self.code_editor.edit_redo(), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.code_editor.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self.code_editor.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self.code_editor.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=lambda: self.code_editor.tag_add(tk.SEL, "1.0", tk.END), accelerator="Ctrl+A")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Analyze Code", command=self._analyze_code, accelerator="F5")
        view_menu.add_separator()
        view_menu.add_command(label="Light Theme", command=lambda: self._change_theme("light"))
        view_menu.add_command(label="Dark Theme", command=lambda: self._change_theme("dark"))
        view_menu.add_separator()
        view_menu.add_command(label="Settings...", command=self._show_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self._new_file())
        self.root.bind("<Control-o>", lambda e: self._load_code())
        self.root.bind("<Control-s>", lambda e: self._save_code())
        self.root.bind("<Control-S>", lambda e: self._save_code_as())
        self.root.bind("<F5>", lambda e: self._analyze_code())
    
    def _show_settings(self):
        """Show the settings dialog."""
        SettingsDialog(self.root)
    
    def _apply_settings(self):
        """Apply current settings to the editor."""
        # Apply editor settings
        self.code_editor.configure(
            font=(self.settings['editor']['font_family'], self.settings['editor']['font_size']),
            wrap=tk.WORD if self.settings['editor']['word_wrap'] else tk.NONE
        )
        
        # Configure tab behavior
        if self.settings['editor']['use_spaces']:
            self.code_editor.bind('<Tab>', lambda e: self._insert_spaces(e))
        else:
            self.code_editor.bind('<Tab>', lambda e: self._insert_tab(e))
        
        # Show/hide line numbers
        if self.settings['editor']['show_line_numbers']:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        else:
            self.line_numbers.pack_forget()
        
        # Apply theme
        self._change_theme(self.settings['theme']['current'])
        
        # Update syntax highlighting colors
        for token_type, color in self.settings['theme']['colors'].items():
            self.syntax_highlighter.text_widget.tag_configure(token_type, foreground=color)
        
        # Reapply syntax highlighting
        self.syntax_highlighter.highlight()
        
        # Set up real-time analysis if enabled
        if self.settings['analysis']['real_time']:
            self._setup_real_time_analysis()
        else:
            self._cancel_real_time_analysis()
    
    def _insert_spaces(self, event):
        """Insert spaces instead of tab."""
        self.code_editor.insert(tk.INSERT, ' ' * self.settings['editor']['tab_size'])
        return 'break'
    
    def _insert_tab(self, event):
        """Insert tab character."""
        self.code_editor.insert(tk.INSERT, '\t')
        return 'break'
    
    def _setup_real_time_analysis(self):
        """Set up real-time code analysis."""
        self._cancel_real_time_analysis()  # Cancel any existing timer
        
        def analyze():
            self._analyze_code()
            if self.settings['analysis']['real_time']:
                self.analysis_timer = self.root.after(
                    self.settings['analysis']['delay'],
                    analyze
                )
        
        self.analysis_timer = self.root.after(
            self.settings['analysis']['delay'],
            analyze
        )
    
    def _cancel_real_time_analysis(self):
        """Cancel real-time code analysis."""
        if hasattr(self, 'analysis_timer'):
            self.root.after_cancel(self.analysis_timer)
            del self.analysis_timer
    
    def _new_file(self):
        """Create a new file."""
        if messagebox.askyesno("New File", "Do you want to save the current file?"):
            self._save_code()
        self._clear_all()
    
    def _show_about(self):
        """Show the about dialog."""
        about_text = """
C Code Error Detection and Recovery System
Version 1.0

A comprehensive tool for analyzing and fixing C code errors.
Features:
- Lexical analysis
- Syntax analysis
- Semantic analysis
- Error recovery
- Syntax highlighting
- Dark/Light themes

Created as a compiler project.
"""
        messagebox.showinfo("About", about_text)
    
    def _show_documentation(self):
        """Show the documentation viewer."""
        DocumentationViewer(self.root)
    
    def _create_toolbar(self):
        """Create the toolbar with action buttons."""
        toolbar = ttk.Frame(self.left_panel)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Create buttons
        ttk.Button(toolbar, text="Analyze", command=self._analyze_code).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Clear", command=self._clear_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self._save_code).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save As", command=self._save_code_as).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Load", command=self._load_code).pack(side=tk.LEFT, padx=2)
        
        # Add theme selector
        ttk.Label(toolbar, text="Theme:").pack(side=tk.LEFT, padx=(10, 2))
        self.theme_var = tk.StringVar(value="light")
        theme_combo = ttk.Combobox(toolbar, textvariable=self.theme_var, values=["light", "dark"])
        theme_combo.pack(side=tk.LEFT, padx=2)
        theme_combo.bind("<<ComboboxSelected>>", self._change_theme)
    
    def _create_code_editor(self):
        """Create the code editor with syntax highlighting."""
        # Create editor frame
        editor_frame = ttk.LabelFrame(self.left_panel, text="C Code Editor")
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create text widget with line numbers
        self.code_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            font=("Consolas", 12),
            undo=True
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        
        # Add line numbers
        self.line_numbers = tk.Text(
            editor_frame,
            width=4,
            padx=3,
            pady=5,
            takefocus=0,
            border=0,
            background='#f0f0f0',
            state='disabled',
            font=("Consolas", 12)
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Bind events
        self.code_editor.bind("<Key>", self._update_line_numbers)
        self.code_editor.bind("<MouseWheel>", self._update_line_numbers)
    
    def _create_error_display(self):
        """Create the error display panel."""
        # Create error display frame
        error_frame = ttk.LabelFrame(self.right_panel, text="Error Analysis")
        error_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for different error types
        self.error_notebook = ttk.Notebook(error_frame)
        self.error_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for different error types
        self.lexical_tab = ttk.Frame(self.error_notebook)
        self.syntax_tab = ttk.Frame(self.error_notebook)
        self.semantic_tab = ttk.Frame(self.error_notebook)
        
        self.error_notebook.add(self.lexical_tab, text="Lexical Errors")
        self.error_notebook.add(self.syntax_tab, text="Syntax Errors")
        self.error_notebook.add(self.semantic_tab, text="Semantic Errors")
        
        # Create error displays for each tab
        self._create_error_tab(self.lexical_tab)
        self._create_error_tab(self.syntax_tab)
        self._create_error_tab(self.semantic_tab)
    
    def _create_error_tab(self, parent):
        """Create an error display tab."""
        # Create treeview for errors
        columns = ("Line", "Column", "Message", "Severity", "Suggestion")
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Store treeview reference
        if parent == self.lexical_tab:
            self.lexical_tree = tree
        elif parent == self.syntax_tab:
            self.syntax_tree = tree
        else:
            self.semantic_tree = tree
    
    def _update_line_numbers(self, event=None):
        """Update the line numbers display."""
        # Get the number of lines in the editor
        lines = self.code_editor.get("1.0", tk.END).count("\n")
        
        # Update line numbers
        self.line_numbers.config(state='normal')
        self.line_numbers.delete("1.0", tk.END)
        for i in range(1, lines + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        self.line_numbers.config(state='disabled')
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # File information
        self.file_info_label = ttk.Label(self.status_bar, text="File: Untitled")
        self.file_info_label.pack(side=tk.LEFT, padx=5)
        
        # Cursor position
        self.cursor_pos_label = ttk.Label(self.status_bar, text="Line: 1, Column: 1")
        self.cursor_pos_label.pack(side=tk.RIGHT, padx=5)
        
        # Error count
        self.error_count_label = ttk.Label(self.status_bar, text="Errors: 0")
        self.error_count_label.pack(side=tk.RIGHT, padx=5)
    
    def _update_status_bar(self, event=None):
        """Update the status bar information."""
        # Update cursor position
        try:
            cursor_pos = self.code_editor.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.cursor_pos_label.config(text=f"Line: {line}, Column: {col}")
        except:
            pass
        
        # Update file information
        file_name = self.file_dialog.get_current_file_name()
        self.file_info_label.config(text=f"File: {file_name}")
        
        # Update error count
        total_errors = (
            len(self.lexical_tree.get_children()) +
            len(self.syntax_tree.get_children()) +
            len(self.semantic_tree.get_children())
        )
        self.error_count_label.config(text=f"Errors: {total_errors}")
    
    def _analyze_code(self):
        """Analyze the code and display errors."""
        # Get code from editor
        code = self.code_editor.get("1.0", tk.END)
        
        # Clear previous errors
        self._clear_errors()
        
        try:
            # Tokenize code
            self.tokenizer = Tokenizer(code)
            tokens = self.tokenizer.tokenize()
            
            # Perform lexical analysis
            lexical_errors = self.lexical_detector.detect_errors(tokens)
            self._display_errors(self.lexical_tree, lexical_errors)
            
            # Perform syntax analysis
            syntax_errors = self.syntax_analyzer.analyze(tokens)
            self._display_errors(self.syntax_tree, syntax_errors)
            
            # Perform semantic analysis
            semantic_errors = self.type_checker.check_types(tokens)
            self._display_errors(self.semantic_tree, semantic_errors)
            
            # Update error counts in notebook tabs
            self._update_error_counts()
            
            # Update status bar
            self._update_status_bar()
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
    
    def _display_errors(self, tree, errors):
        """Display errors in a treeview."""
        for error in errors:
            tree.insert("", tk.END, values=(
                error.line,
                error.column,
                error.message,
                error.severity,
                error.suggestion
            ))
    
    def _update_error_counts(self):
        """Update error counts in notebook tabs."""
        lexical_count = len(self.lexical_tree.get_children())
        syntax_count = len(self.syntax_tree.get_children())
        semantic_count = len(self.semantic_tree.get_children())
        
        self.error_notebook.tab(0, text=f"Lexical Errors ({lexical_count})")
        self.error_notebook.tab(1, text=f"Syntax Errors ({syntax_count})")
        self.error_notebook.tab(2, text=f"Semantic Errors ({semantic_count})")
    
    def _clear_errors(self):
        """Clear all error displays."""
        self.lexical_tree.delete(*self.lexical_tree.get_children())
        self.syntax_tree.delete(*self.syntax_tree.get_children())
        self.semantic_tree.delete(*self.semantic_tree.get_children())
        self._update_error_counts()
    
    def _clear_all(self):
        """Clear the code editor and error displays."""
        self.code_editor.delete("1.0", tk.END)
        self._clear_errors()
        self._update_line_numbers()
        self._update_title()
        self._update_status_bar()
    
    def _save_code(self):
        """Save the code to a file."""
        content = self.code_editor.get("1.0", tk.END)
        if self.file_dialog.save_file(content):
            self._update_title()
    
    def _save_code_as(self):
        """Save the code to a new file."""
        content = self.code_editor.get("1.0", tk.END)
        if self.file_dialog.save_file_as(content):
            self._update_title()
    
    def _load_code(self):
        """Load code from a file."""
        content = self.file_dialog.load_file()
        if content is not None:
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert("1.0", content)
            self._update_line_numbers()
            self._update_title()
            self.syntax_highlighter.highlight()
            self._update_status_bar()
    
    def _update_title(self):
        """Update the window title with current file name."""
        file_name = self.file_dialog.get_current_file_name()
        self.root.title(f"{file_name} - C Code Error Detection and Recovery System")
    
    def _change_theme(self, theme=None):
        """Change the application theme."""
        if theme is None:
            theme = self.theme_var.get()
        else:
            self.theme_var.set(theme)
        
        if theme == "dark":
            self.root.configure(background='#2b2b2b')
            self.code_editor.configure(
                background='#2b2b2b',
                foreground='#ffffff',
                insertbackground='#ffffff'
            )
            self.line_numbers.configure(
                background='#3b3b3b',
                foreground='#ffffff'
            )
            # Update syntax highlighting colors for dark theme
            self.syntax_highlighter.text_widget.tag_configure('keyword', foreground='#569CD6')
            self.syntax_highlighter.text_widget.tag_configure('type', foreground='#569CD6')
            self.syntax_highlighter.text_widget.tag_configure('string', foreground='#CE9178')
            self.syntax_highlighter.text_widget.tag_configure('comment', foreground='#6A9955')
            self.syntax_highlighter.text_widget.tag_configure('number', foreground='#B5CEA8')
            self.syntax_highlighter.text_widget.tag_configure('operator', foreground='#D4D4D4')
            self.syntax_highlighter.text_widget.tag_configure('preprocessor', foreground='#C586C0')
        else:
            self.root.configure(background='#f0f0f0')
            self.code_editor.configure(
                background='#ffffff',
                foreground='#000000',
                insertbackground='#000000'
            )
            self.line_numbers.configure(
                background='#f0f0f0',
                foreground='#000000'
            )
            # Update syntax highlighting colors for light theme
            self.syntax_highlighter.text_widget.tag_configure('keyword', foreground='#0000FF')
            self.syntax_highlighter.text_widget.tag_configure('type', foreground='#0000FF')
            self.syntax_highlighter.text_widget.tag_configure('string', foreground='#008000')
            self.syntax_highlighter.text_widget.tag_configure('comment', foreground='#808080')
            self.syntax_highlighter.text_widget.tag_configure('number', foreground='#FF0000')
            self.syntax_highlighter.text_widget.tag_configure('operator', foreground='#000000')
            self.syntax_highlighter.text_widget.tag_configure('preprocessor', foreground='#800080')
        
        # Reapply syntax highlighting
        self.syntax_highlighter.highlight()

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main() 