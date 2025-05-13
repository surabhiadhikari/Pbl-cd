"""
Lexical error detection for C code.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from .tokenizer import Token, TokenType

@dataclass
class LexicalError:
    line: int
    column: int
    message: str
    severity: str  # 'error', 'warning', 'info'
    suggestion: str = ''

class LexicalErrorDetector:
    def __init__(self):
        self.errors: List[LexicalError] = []
        self.valid_operators = {'+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>='}
        self.valid_delimiters = {';', ',', '(', ')', '{', '}', '[', ']'}
    
    def detect_errors(self, tokens: List[Token]) -> List[LexicalError]:
        """Detect lexical errors in the token stream."""
        self.errors.clear()
        
        for i, token in enumerate(tokens):
            # Check for invalid identifiers
            if token.type == TokenType.IDENTIFIER:
                self._check_identifier(token)
            
            # Check for invalid numbers
            elif token.type in (TokenType.INTEGER, TokenType.FLOAT_LITERAL):
                self._check_number(token)
            
            # Check for invalid operators
            elif token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE):
                self._check_operator(token, tokens, i)
            
            # Check for missing semicolons
            if i > 0 and self._should_have_semicolon(tokens[i-1], token):
                self.errors.append(LexicalError(
                    line=token.line,
                    column=token.column,
                    message="Missing semicolon",
                    severity="error",
                    suggestion="Add a semicolon at the end of the previous statement"
                ))
        
        return self.errors
    
    def _check_identifier(self, token: Token):
        """Check for invalid identifier patterns."""
        # Check if identifier starts with a number
        if token.value[0].isdigit():
            self.errors.append(LexicalError(
                line=token.line,
                column=token.column,
                message="Identifier cannot start with a number",
                severity="error",
                suggestion=f"Rename '{token.value}' to start with a letter or underscore"
            ))
        
        # Check for invalid characters
        invalid_chars = set(token.value) - set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
        if invalid_chars:
            self.errors.append(LexicalError(
                line=token.line,
                column=token.column,
                message=f"Invalid characters in identifier: {invalid_chars}",
                severity="error",
                suggestion=f"Remove invalid characters from '{token.value}'"
            ))
    
    def _check_number(self, token: Token):
        """Check for invalid number formats."""
        if token.type == TokenType.FLOAT_LITERAL:
            # Check for multiple decimal points
            if token.value.count('.') > 1:
                self.errors.append(LexicalError(
                    line=token.line,
                    column=token.column,
                    message="Invalid float literal: multiple decimal points",
                    severity="error",
                    suggestion="Use only one decimal point in float literals"
                ))
            
            # Check for trailing decimal point
            if token.value.endswith('.'):
                self.errors.append(LexicalError(
                    line=token.line,
                    column=token.column,
                    message="Invalid float literal: trailing decimal point",
                    severity="warning",
                    suggestion="Add a digit after the decimal point or remove it"
                ))
    
    def _check_operator(self, token: Token, tokens: List[Token], index: int):
        """Check for invalid operator usage."""
        # Check for consecutive operators
        if index > 0 and tokens[index-1].type in (TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE):
            self.errors.append(LexicalError(
                line=token.line,
                column=token.column,
                message="Consecutive operators",
                severity="error",
                suggestion="Remove one of the consecutive operators"
            ))
    
    def _should_have_semicolon(self, prev_token: Token, current_token: Token) -> bool:
        """Check if a semicolon should be present between two tokens."""
        # Don't need semicolon after these tokens
        no_semicolon_after = {
            TokenType.LBRACE,
            TokenType.RBRACE,
            TokenType.SEMICOLON,
            TokenType.IF,
            TokenType.ELSE,
            TokenType.WHILE,
            TokenType.FOR
        }
        
        # Need semicolon after these tokens
        need_semicolon_after = {
            TokenType.IDENTIFIER,
            TokenType.INTEGER,
            TokenType.FLOAT_LITERAL,
            TokenType.CHAR_LITERAL,
            TokenType.STRING_LITERAL,
            TokenType.RPAREN,
            TokenType.RBRACKET
        }
        
        return (prev_token.type in need_semicolon_after and 
                current_token.type not in no_semicolon_after and
                current_token.type != TokenType.SEMICOLON) 