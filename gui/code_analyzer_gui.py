import tkinter as tk
from tkinter import ttk, scrolledtext
import re
from documentation_viewer import DocumentationViewer

class CodeAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("C Code Analyzer")
        self.root.geometry("1200x800")
        
        # Add menu bar with Help
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.open_documentation)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        
        # Create main container
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for code input
        self.input_frame = ttk.LabelFrame(self.main_container, text="Code Input")
        self.main_container.add(self.input_frame, weight=1)
        
        # Create frame for line numbers and code editor
        self.editor_frame = ttk.Frame(self.input_frame)
        self.editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Line numbers
        self.line_numbers = tk.Text(
            self.editor_frame,
            width=4,
            padx=3,
            pady=5,
            takefocus=0,
            border=0,
            background='#f0f0f0',
            state='disabled',
            font=("Consolas", 11)
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Code editor
        self.code_editor = scrolledtext.ScrolledText(
            self.editor_frame,
            wrap=tk.NONE,
            font=("Consolas", 11),
            width=50,
            height=30
        )
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add placeholder text
        self.code_editor.insert(tk.END, "Enter your C code here...")
        self.code_editor.bind("<FocusIn>", self._on_focus_in)
        
        # Bind events for line numbers
        self.code_editor.bind("<Key>", self._update_line_numbers)
        self.code_editor.bind("<MouseWheel>", self._update_line_numbers)
        self.code_editor.bind("<Button-1>", self._update_line_numbers)
        
        # Initial line numbers
        self._update_line_numbers()
        
        # Right panel for analysis results
        self.result_frame = ttk.LabelFrame(self.main_container, text="Analysis Results")
        self.main_container.add(self.result_frame, weight=1)
        
        # Create notebook for different analysis views
        self.notebook = ttk.Notebook(self.result_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Lexical Analysis tab
        self.lexical_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.lexical_frame, text="Lexical Analysis")
        self.lexical_text = scrolledtext.ScrolledText(
            self.lexical_frame,
            wrap=tk.WORD,
            font=("Consolas", 11)
        )
        self.lexical_text.pack(fill=tk.BOTH, expand=True)
        
        # Syntax Analysis tab
        self.syntax_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.syntax_frame, text="Syntax Analysis")
        self.syntax_text = scrolledtext.ScrolledText(
            self.syntax_frame,
            wrap=tk.WORD,
            font=("Consolas", 11)
        )
        self.syntax_text.pack(fill=tk.BOTH, expand=True)
        
        # Semantic Analysis tab
        self.semantic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.semantic_frame, text="Semantic Analysis")
        self.semantic_text = scrolledtext.ScrolledText(
            self.semantic_frame,
            wrap=tk.WORD,
            font=("Consolas", 11)
        )
        self.semantic_text.pack(fill=tk.BOTH, expand=True)
        
        # Recovery Analysis tab
        self.recovery_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recovery_frame, text="Recovery Analysis")
        self.recovery_text = scrolledtext.ScrolledText(
            self.recovery_frame,
            wrap=tk.WORD,
            font=("Consolas", 11)
        )
        self.recovery_text.pack(fill=tk.BOTH, expand=True)
        
        # Suggestions tab
        self.suggestions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.suggestions_frame, text="Suggestions")
        self.suggestions_text = scrolledtext.ScrolledText(
            self.suggestions_frame,
            wrap=tk.WORD,
            font=("Consolas", 11)
        )
        self.suggestions_text.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Analyze button
        self.analyze_button = ttk.Button(
            self.button_frame,
            text="Analyze Code",
            command=self.analyze_code
        )
        self.analyze_button.pack(side=tk.RIGHT, padx=5)
        
        # Clear Results button
        self.clear_results_button = ttk.Button(
            self.button_frame,
            text="Clear Results",
            command=self.clear_results
        )
        self.clear_results_button.pack(side=tk.RIGHT, padx=5)
        
        # Clear Code button
        self.clear_code_button = ttk.Button(
            self.button_frame,
            text="Clear Code",
            command=self.clear_code
        )
        self.clear_code_button.pack(side=tk.RIGHT, padx=5)
        
        # Add variables for tracking
        self.declared_variables = set()
        self.valid_c_tokens = set([
            'int', 'char', 'float', 'double', 'void', 'if', 'else', 'while', 'for',
            'return', 'printf', 'scanf', 'main', 'include', 'stdio.h', 'stdlib.h'
        ])
    
    def open_documentation(self):
        DocumentationViewer(self.root)
    
    def _update_line_numbers(self, event=None):
        """Update the line numbers display."""
        # Get the number of lines in the editor
        line_count = self.code_editor.get("1.0", tk.END).count("\n")
        
        # Update line numbers
        self.line_numbers.config(state='normal')
        self.line_numbers.delete("1.0", tk.END)
        for i in range(1, line_count + 1):
            # Right-align the line numbers
            self.line_numbers.insert(tk.END, f"{i:3d}\n")
        self.line_numbers.config(state='disabled')
        
        # Synchronize scrolling
        self.line_numbers.yview_moveto(self.code_editor.yview()[0])
    
    def _on_focus_in(self, event):
        """Clear placeholder text when the user clicks in the text area."""
        if self.code_editor.get("1.0", tk.END).strip() == "Enter your C code here...":
            self.code_editor.delete("1.0", tk.END)
            self._update_line_numbers()
    
    def clear_code(self):
        """Clear the code input area."""
        self.code_editor.delete("1.0", tk.END)
        self.code_editor.insert(tk.END, "Enter your C code here...")
        self._update_line_numbers()
    
    def analyze_code(self):
        """Analyze the code and display results."""
        code = self.code_editor.get("1.0", tk.END)
        
        # Don't analyze if only placeholder text is present
        if code.strip() == "Enter your C code here...":
            return
        
        # Clear previous results and tracking
        self.clear_results()
        self.declared_variables.clear()
        
        # Perform lexical analysis
        self.perform_lexical_analysis(code)
        
        # Perform syntax analysis with recovery
        self.perform_syntax_analysis(code)
        
        # Perform semantic analysis
        self.perform_semantic_analysis(code)
        
        # Generate suggestions
        self.generate_suggestions(code)
    
    def perform_lexical_analysis(self, code):
        """Perform lexical analysis on the code."""
        tokens = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for invalid characters
            invalid_chars = re.findall(r'[^a-zA-Z0-9\s\{\}\(\)\[\]\;\:\,\"\'\+\-\*\/\%\=\!\<\>\&\|\^\.\#]', line)
            if invalid_chars:
                tokens.append(f"Line {i}: Error - Invalid characters found: {', '.join(set(invalid_chars))}")
            
            # Check for common lexical errors
            if '//' in line and '/*' in line:
                tokens.append(f"Line {i}: Warning - Mixed comment styles")
            if len(line) > 100:
                tokens.append(f"Line {i}: Warning - Line too long")
            
            # Check for invalid tokens (excluding numbers and valid identifiers)
            words = re.findall(r'\b\w+\b', line)
            for word in words:
                # Skip if it's a number
                if word.isdigit():
                    continue
                # Skip if it's a valid identifier
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', word):
                    continue
                # Skip if it's a valid C token
                if word in self.valid_c_tokens:
                    continue
                # If none of the above, it's an invalid token
                tokens.append(f"Line {i}: Error - Invalid token: {word}")
            
            # Track variable declarations
            var_decl = re.search(r'\b(int|char|float|double)\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
            if var_decl:
                self.declared_variables.add(var_decl.group(2))
        
        self.lexical_text.insert(tk.END, "Lexical Analysis Results:\n\n")
        if tokens:
            for token in tokens:
                self.lexical_text.insert(tk.END, f"{token}\n")
        else:
            self.lexical_text.insert(tk.END, "No lexical issues found.\n")
    
    def perform_syntax_analysis(self, code):
        """Perform syntax analysis on the code with recovery."""
        errors = []
        recovery_actions = []
        lines = code.split('\n')
        brace_stack = []
        paren_stack = []
        in_panic_mode = False
        panic_mode_start = 0
        main_brace_line = None
        
        for i, line in enumerate(lines, 1):
            # Track main function's opening brace
            if 'main()' in line and '{' in line:
                main_brace_line = i
            
            # Panic mode recovery
            if in_panic_mode:
                # Look for synchronizing tokens
                if ';' in line or '{' in line or '}' in line:
                    recovery_actions.append(f"Panic Mode Recovery: Skipped from line {panic_mode_start} to line {i}")
                    in_panic_mode = False
                continue
            
            # Check for basic syntax errors
            for char in line:
                if char == '{':
                    brace_stack.append(i)
                elif char == '}':
                    if not brace_stack:
                        errors.append(f"Line {i}: Error - Unexpected closing brace")
                        in_panic_mode = True
                        panic_mode_start = i
                    else:
                        brace_stack.pop()
                elif char == '(':
                    paren_stack.append(i)
                elif char == ')':
                    if not paren_stack:
                        errors.append(f"Line {i}: Error - Unexpected closing parenthesis")
                        in_panic_mode = True
                        panic_mode_start = i
                    else:
                        paren_stack.pop()
            
            # Phrase-level recovery for missing semicolons
            if line.strip() and not line.strip().endswith(';') and not line.strip().endswith('{') and not line.strip().endswith('}') and not line.strip().startswith('#'):
                errors.append(f"Line {i}: Error - Missing semicolon")
                recovery_actions.append(f"Phrase-Level Recovery: Suggested adding semicolon at line {i}")
                # Show how the line would look with the fix
                fixed_line = line.rstrip() + ";"
                recovery_actions.append(f"  Original: {line.strip()}")
                recovery_actions.append(f"  Fixed:    {fixed_line.strip()}")
        
        # Check for unclosed braces/parentheses
        for line_num in brace_stack:
            errors.append(f"Line {line_num}: Error - Unclosed brace")
            # Special handling for main function's closing brace
            if line_num == main_brace_line:
                # Find the last line of the function (return statement)
                last_line = len(lines)
                recovery_actions.append(f"Phrase-Level Recovery: Add closing brace after line {last_line}")
            else:
                # Regular brace handling
                opening_line = line_num
                recovery_actions.append(f"Phrase-Level Recovery: Add closing brace after line {opening_line}")
        
        for line_num in paren_stack:
            errors.append(f"Line {line_num}: Error - Unclosed parenthesis")
            # Find the corresponding opening line
            opening_line = line_num
            recovery_actions.append(f"Phrase-Level Recovery: Add closing parenthesis after line {opening_line}")
        
        # Display syntax analysis results
        self.syntax_text.insert(tk.END, "Syntax Analysis Results:\n\n")
        if errors:
            for error in errors:
                self.syntax_text.insert(tk.END, f"{error}\n")
        else:
            self.syntax_text.insert(tk.END, "No syntax issues found.\n")
        
        # Display recovery analysis
        self.recovery_text.insert(tk.END, "Recovery Analysis Results:\n\n")
        if recovery_actions:
            for action in recovery_actions:
                self.recovery_text.insert(tk.END, f"{action}\n")
        else:
            self.recovery_text.insert(tk.END, "No recovery actions needed.\n")
    
    def perform_semantic_analysis(self, code):
        """Perform semantic analysis on the code."""
        warnings = []
        lines = code.split('\n')
        
        # Check for common semantic issues
        if 'printf' in code and '<stdio.h>' not in code:
            warnings.append("Warning: printf used without including stdio.h")
        if 'main' not in code:
            warnings.append("Error: No main function found")
        
        # Check for undeclared variables
        for i, line in enumerate(lines, 1):
            # Skip preprocessor directives
            if line.strip().startswith('#'):
                continue
                
            # Skip string literals
            line = re.sub(r'"[^"]*"', '', line)
            
            # Skip format specifiers in printf
            line = re.sub(r'%[a-zA-Z]', '', line)
            
            # Find all variable usages
            var_usages = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', line)
            for var in var_usages:
                if var not in self.declared_variables and var not in self.valid_c_tokens:
                    warnings.append(f"Line {i}: Error - Undeclared variable: {var}")
        
        self.semantic_text.insert(tk.END, "Semantic Analysis Results:\n\n")
        if warnings:
            for warning in warnings:
                self.semantic_text.insert(tk.END, f"{warning}\n")
        else:
            self.semantic_text.insert(tk.END, "No semantic issues found.\n")
    
    def generate_suggestions(self, code):
        """Generate suggestions for improving the code."""
        suggestions = []
        
        # Generate suggestions based on analysis
        if 'printf' in code and '<stdio.h>' not in code:
            suggestions.append("Add #include <stdio.h> at the beginning of the file")
        if code.count('{') != code.count('}'):
            suggestions.append("Check for missing or extra braces")
        
        # Additional suggestions
        if re.search(r'\b(if|while|for)\s*\([^=]*=[^=]', code):
            suggestions.append("Use == instead of = for comparisons in conditions")
        if re.search(r'\bwhile\s*\(\s*1\s*\)', code):
            suggestions.append("Consider adding a break condition to prevent infinite loops")
        if re.search(r'\b(int|char|float|double)\s+\w+\s*;', code):
            suggestions.append("Initialize variables when declaring them")
        
        self.suggestions_text.insert(tk.END, "Suggestions for Improvement:\n\n")
        if suggestions:
            for suggestion in suggestions:
                self.suggestions_text.insert(tk.END, f"• {suggestion}\n")
        else:
            self.suggestions_text.insert(tk.END, "No suggestions. Your code looks good!\n")
    
    def clear_results(self):
        """Clear all analysis results."""
        self.lexical_text.delete("1.0", tk.END)
        self.syntax_text.delete("1.0", tk.END)
        self.semantic_text.delete("1.0", tk.END)
        self.recovery_text.delete("1.0", tk.END)
        self.suggestions_text.delete("1.0", tk.END)

def main():
    root = tk.Tk()
    app = CodeAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 