# C Code Error Detection and Recovery System

An advanced C code analysis tool that detects and helps recover from various types of errors in C code.

## Features

- Lexical Analysis
- Syntax Analysis
- Semantic Analysis
- Error Recovery
- GUI Interface
- Code Style Checking
- Real-time Error Detection

## Project Structure

```
compiler/
├── lexer/          # Lexical analysis components
├── parser/         # Syntax analysis components
├── semantic/       # Semantic analysis components
├── gui/            # Graphical user interface
├── utils/          # Utility functions and helpers
├── tests/          # Test cases and test utilities
└── docs/           # Documentation
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main application:
```bash
python -m compiler.gui.main_window
```

## Testing

Run tests using pytest:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 