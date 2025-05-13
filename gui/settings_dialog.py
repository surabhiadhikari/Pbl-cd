"""
Settings dialog for customizing editor appearance and behavior.
"""

import tkinter as tk
from tkinter import ttk, font
import json
from pathlib import Path

class SettingsDialog:
    def __init__(self, parent):
        self.parent = parent
        self.settings = self._load_settings()
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create notebook for settings categories
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create settings tabs
        self._create_editor_tab()
        self._create_theme_tab()
        self._create_analysis_tab()
        
        # Create buttons
        self._create_buttons()
        
        # Center dialog on parent window
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_editor_tab(self):
        """Create the editor settings tab."""
        editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(editor_frame, text="Editor")
        
        # Font settings
        font_frame = ttk.LabelFrame(editor_frame, text="Font")
        font_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Font family
        ttk.Label(font_frame, text="Font Family:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.font_family = ttk.Combobox(font_frame, values=sorted(font.families()))
        self.font_family.set(self.settings['editor']['font_family'])
        self.font_family.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Font size
        ttk.Label(font_frame, text="Font Size:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.font_size = ttk.Spinbox(font_frame, from_=8, to=72, width=5)
        self.font_size.set(self.settings['editor']['font_size'])
        self.font_size.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Tab settings
        tab_frame = ttk.LabelFrame(editor_frame, text="Tab Settings")
        tab_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Tab size
        ttk.Label(tab_frame, text="Tab Size:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.tab_size = ttk.Spinbox(tab_frame, from_=2, to=8, width=5)
        self.tab_size.set(self.settings['editor']['tab_size'])
        self.tab_size.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Use spaces instead of tabs
        self.use_spaces = tk.BooleanVar(value=self.settings['editor']['use_spaces'])
        ttk.Checkbutton(tab_frame, text="Use Spaces Instead of Tabs", variable=self.use_spaces).grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W
        )
        
        # Line numbers
        self.show_line_numbers = tk.BooleanVar(value=self.settings['editor']['show_line_numbers'])
        ttk.Checkbutton(editor_frame, text="Show Line Numbers", variable=self.show_line_numbers).pack(
            anchor=tk.W, padx=5, pady=5
        )
        
        # Word wrap
        self.word_wrap = tk.BooleanVar(value=self.settings['editor']['word_wrap'])
        ttk.Checkbutton(editor_frame, text="Word Wrap", variable=self.word_wrap).pack(
            anchor=tk.W, padx=5, pady=5
        )
    
    def _create_theme_tab(self):
        """Create the theme settings tab."""
        theme_frame = ttk.Frame(self.notebook)
        self.notebook.add(theme_frame, text="Theme")
        
        # Theme selection
        ttk.Label(theme_frame, text="Theme:").pack(anchor=tk.W, padx=5, pady=5)
        self.theme = ttk.Combobox(theme_frame, values=["light", "dark"])
        self.theme.set(self.settings['theme']['current'])
        self.theme.pack(fill=tk.X, padx=5, pady=5)
        
        # Syntax highlighting colors
        colors_frame = ttk.LabelFrame(theme_frame, text="Syntax Highlighting Colors")
        colors_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create color pickers for each token type
        self.color_vars = {}
        row = 0
        for token_type, color in self.settings['theme']['colors'].items():
            ttk.Label(colors_frame, text=f"{token_type.title()}:").grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)
            self.color_vars[token_type] = tk.StringVar(value=color)
            ttk.Entry(colors_frame, textvariable=self.color_vars[token_type], width=10).grid(
                row=row, column=1, padx=5, pady=2, sticky=tk.W
            )
            row += 1
    
    def _create_analysis_tab(self):
        """Create the analysis settings tab."""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Analysis")
        
        # Analysis options
        options_frame = ttk.LabelFrame(analysis_frame, text="Analysis Options")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Enable real-time analysis
        self.real_time_analysis = tk.BooleanVar(value=self.settings['analysis']['real_time'])
        ttk.Checkbutton(options_frame, text="Enable Real-time Analysis", variable=self.real_time_analysis).pack(
            anchor=tk.W, padx=5, pady=5
        )
        
        # Analysis delay
        ttk.Label(options_frame, text="Analysis Delay (ms):").pack(anchor=tk.W, padx=5, pady=5)
        self.analysis_delay = ttk.Spinbox(options_frame, from_=100, to=5000, increment=100, width=5)
        self.analysis_delay.set(self.settings['analysis']['delay'])
        self.analysis_delay.pack(anchor=tk.W, padx=5, pady=5)
        
        # Error severity levels
        severity_frame = ttk.LabelFrame(analysis_frame, text="Error Severity Levels")
        severity_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.severity_vars = {}
        for error_type, severity in self.settings['analysis']['severity'].items():
            ttk.Label(severity_frame, text=f"{error_type.title()}:").pack(anchor=tk.W, padx=5, pady=2)
            self.severity_vars[error_type] = tk.StringVar(value=severity)
            ttk.Combobox(severity_frame, textvariable=self.severity_vars[error_type],
                        values=["error", "warning", "info"]).pack(fill=tk.X, padx=5, pady=2)
    
    def _create_buttons(self):
        """Create the dialog buttons."""
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="OK", command=self._save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Apply", command=self._apply_settings).pack(side=tk.RIGHT, padx=5)
    
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
    
    def _save_settings(self):
        """Save settings to file."""
        settings = {
            'editor': {
                'font_family': self.font_family.get(),
                'font_size': int(self.font_size.get()),
                'tab_size': int(self.tab_size.get()),
                'use_spaces': self.use_spaces.get(),
                'show_line_numbers': self.show_line_numbers.get(),
                'word_wrap': self.word_wrap.get()
            },
            'theme': {
                'current': self.theme.get(),
                'colors': {token_type: var.get() for token_type, var in self.color_vars.items()}
            },
            'analysis': {
                'real_time': self.real_time_analysis.get(),
                'delay': int(self.analysis_delay.get()),
                'severity': {error_type: var.get() for error_type, var in self.severity_vars.items()}
            }
        }
        
        # Create settings directory if it doesn't exist
        settings_dir = Path.home() / '.c_analyzer'
        settings_dir.mkdir(exist_ok=True)
        
        # Save settings to file
        settings_file = settings_dir / 'settings.json'
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        
        # Apply settings and close dialog
        self._apply_settings()
        self.dialog.destroy()
    
    def _apply_settings(self):
        """Apply current settings to the editor."""
        # Notify parent window to apply settings
        self.parent.event_generate('<<SettingsChanged>>') 