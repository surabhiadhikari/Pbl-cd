"""
Token definitions and tokenization logic for C code.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Keywords
    INT = auto()
    CHAR = auto()
    FLOAT = auto()
    VOID = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    GREATER = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    
    # Delimiters
    SEMICOLON = auto()
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    
    # Others
    IDENTIFIER = auto()
    INTEGER = auto()
    FLOAT_LITERAL = auto()
    CHAR_LITERAL = auto()
    STRING_LITERAL = auto()
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class Tokenizer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source[0] if source else None
        
        # Keywords mapping
        self.keywords = {
            'int': TokenType.INT,
            'char': TokenType.CHAR,
            'float': TokenType.FLOAT,
            'void': TokenType.VOID,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'return': TokenType.RETURN
        }
    
    def advance(self):
        """Move to the next character in the source code."""
        self.position += 1
        self.column += 1
        
        if self.position >= len(self.source):
            self.current_char = None
        else:
            self.current_char = self.source[self.position]
            
            if self.current_char == '\n':
                self.line += 1
                self.column = 0
    
    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        """Skip single-line and multi-line comments."""
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char and self.current_char != '\n':
                self.advance()
        elif self.current_char == '/' and self.peek() == '*':
            self.advance()  # Skip '/'
            self.advance()  # Skip '*'
            while self.current_char and not (self.current_char == '*' and self.peek() == '/'):
                self.advance()
            if self.current_char:
                self.advance()  # Skip '*'
                self.advance()  # Skip '/'
    
    def peek(self) -> Optional[str]:
        """Look at the next character without consuming it."""
        peek_pos = self.position + 1
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def get_identifier(self) -> Token:
        """Get an identifier or keyword token."""
        result = ''
        start_column = self.column
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        token_type = self.keywords.get(result, TokenType.IDENTIFIER)
        return Token(token_type, result, self.line, start_column)
    
    def get_number(self) -> Token:
        """Get a number token (integer or float)."""
        result = ''
        start_column = self.column
        is_float = False
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float:  # Second decimal point
                    break
                is_float = True
            result += self.current_char
            self.advance()
        
        token_type = TokenType.FLOAT_LITERAL if is_float else TokenType.INTEGER
        return Token(token_type, result, self.line, start_column)
    
    def get_next_token(self) -> Token:
        """Get the next token from the source code."""
        while self.current_char:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Skip comments
            if self.current_char == '/':
                if self.peek() in ['/', '*']:
                    self.skip_comment()
                    continue
            
            # Identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                return self.get_identifier()
            
            # Numbers
            if self.current_char.isdigit():
                return self.get_number()
            
            # Operators and delimiters
            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', self.line, self.column - 1)
            
            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', self.line, self.column - 1)
            
            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MULTIPLY, '*', self.line, self.column - 1)
            
            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, '/', self.line, self.column - 1)
            
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUAL, '==', self.line, self.column - 2)
                return Token(TokenType.ASSIGN, '=', self.line, self.column - 1)
            
            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';', self.line, self.column - 1)
            
            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', self.line, self.column - 1)
            
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', self.line, self.column - 1)
            
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', self.line, self.column - 1)
            
            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{', self.line, self.column - 1)
            
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}', self.line, self.column - 1)
            
            if self.current_char == '[':
                self.advance()
                return Token(TokenType.LBRACKET, '[', self.line, self.column - 1)
            
            if self.current_char == ']':
                self.advance()
                return Token(TokenType.RBRACKET, ']', self.line, self.column - 1)
            
            # If we get here, we have an invalid character
            raise SyntaxError(f"Invalid character '{self.current_char}' at line {self.line}, column {self.column}")
        
        return Token(TokenType.EOF, '', self.line, self.column)
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code."""
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens 