"""
Syntax analysis for C code.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from ..lexer.tokenizer import Token, TokenType

@dataclass
class SyntaxError:
    line: int
    column: int
    message: str
    severity: str  # 'error', 'warning', 'info'
    suggestion: str = ''

class SyntaxAnalyzer:
    def __init__(self):
        self.errors: List[SyntaxError] = []
        self.current_token_index = 0
        self.tokens: List[Token] = []
    
    def analyze(self, tokens: List[Token]) -> List[SyntaxError]:
        """Analyze the syntax of the token stream."""
        self.errors.clear()
        self.tokens = tokens
        self.current_token_index = 0
        
        try:
            self._parse_program()
        except Exception as e:
            self.errors.append(SyntaxError(
                line=self._current_token().line,
                column=self._current_token().column,
                message=f"Unexpected error: {str(e)}",
                severity="error"
            ))
        
        return self.errors
    
    def _current_token(self) -> Token:
        """Get the current token."""
        if self.current_token_index >= len(self.tokens):
            return self.tokens[-1]  # Return EOF token
        return self.tokens[self.current_token_index]
    
    def _next_token(self) -> Token:
        """Move to the next token and return it."""
        self.current_token_index += 1
        return self._current_token()
    
    def _expect(self, token_type: TokenType, error_message: str) -> bool:
        """Check if the current token matches the expected type."""
        if self._current_token().type == token_type:
            self._next_token()
            return True
        
        self.errors.append(SyntaxError(
            line=self._current_token().line,
            column=self._current_token().column,
            message=error_message,
            severity="error",
            suggestion=f"Expected {token_type.name}"
        ))
        return False
    
    def _parse_program(self):
        """Parse the entire program."""
        while self._current_token().type != TokenType.EOF:
            if self._current_token().type in (TokenType.INT, TokenType.CHAR, TokenType.FLOAT, TokenType.VOID):
                self._parse_function_declaration()
            else:
                self._parse_statement()
    
    def _parse_function_declaration(self):
        """Parse a function declaration."""
        # Parse return type
        return_type = self._current_token()
        self._next_token()
        
        # Parse function name
        if not self._expect(TokenType.IDENTIFIER, "Expected function name"):
            return
        
        # Parse parameters
        if not self._expect(TokenType.LPAREN, "Expected '(' after function name"):
            return
        
        self._parse_parameter_list()
        
        if not self._expect(TokenType.RPAREN, "Expected ')' after parameter list"):
            return
        
        # Parse function body
        if not self._expect(TokenType.LBRACE, "Expected '{' for function body"):
            return
        
        self._parse_block()
        
        if not self._expect(TokenType.RBRACE, "Expected '}' to end function body"):
            return
    
    def _parse_parameter_list(self):
        """Parse a parameter list."""
        if self._current_token().type == TokenType.RPAREN:
            return
        
        while True:
            # Parse parameter type
            if self._current_token().type not in (TokenType.INT, TokenType.CHAR, TokenType.FLOAT):
                self.errors.append(SyntaxError(
                    line=self._current_token().line,
                    column=self._current_token().column,
                    message="Invalid parameter type",
                    severity="error",
                    suggestion="Parameter type must be int, char, or float"
                ))
                return
            
            self._next_token()
            
            # Parse parameter name
            if not self._expect(TokenType.IDENTIFIER, "Expected parameter name"):
                return
            
            # Check for more parameters
            if self._current_token().type == TokenType.COMMA:
                self._next_token()
                continue
            break
    
    def _parse_block(self):
        """Parse a block of statements."""
        while self._current_token().type != TokenType.RBRACE:
            self._parse_statement()
    
    def _parse_statement(self):
        """Parse a statement."""
        token = self._current_token()
        
        if token.type == TokenType.IF:
            self._parse_if_statement()
        elif token.type == TokenType.WHILE:
            self._parse_while_statement()
        elif token.type == TokenType.FOR:
            self._parse_for_statement()
        elif token.type == TokenType.RETURN:
            self._parse_return_statement()
        elif token.type in (TokenType.INT, TokenType.CHAR, TokenType.FLOAT):
            self._parse_variable_declaration()
        elif token.type == TokenType.IDENTIFIER:
            self._parse_assignment_or_function_call()
        else:
            self.errors.append(SyntaxError(
                line=token.line,
                column=token.column,
                message="Invalid statement",
                severity="error",
                suggestion="Expected a valid statement"
            ))
            self._next_token()
    
    def _parse_if_statement(self):
        """Parse an if statement."""
        self._next_token()  # Skip 'if'
        
        if not self._expect(TokenType.LPAREN, "Expected '(' after if"):
            return
        
        self._parse_expression()
        
        if not self._expect(TokenType.RPAREN, "Expected ')' after condition"):
            return
        
        if not self._expect(TokenType.LBRACE, "Expected '{' for if body"):
            return
        
        self._parse_block()
        
        if not self._expect(TokenType.RBRACE, "Expected '}' to end if body"):
            return
        
        if self._current_token().type == TokenType.ELSE:
            self._next_token()
            
            if not self._expect(TokenType.LBRACE, "Expected '{' for else body"):
                return
            
            self._parse_block()
            
            if not self._expect(TokenType.RBRACE, "Expected '}' to end else body"):
                return
    
    def _parse_while_statement(self):
        """Parse a while statement."""
        self._next_token()  # Skip 'while'
        
        if not self._expect(TokenType.LPAREN, "Expected '(' after while"):
            return
        
        self._parse_expression()
        
        if not self._expect(TokenType.RPAREN, "Expected ')' after condition"):
            return
        
        if not self._expect(TokenType.LBRACE, "Expected '{' for while body"):
            return
        
        self._parse_block()
        
        if not self._expect(TokenType.RBRACE, "Expected '}' to end while body"):
            return
    
    def _parse_for_statement(self):
        """Parse a for statement."""
        self._next_token()  # Skip 'for'
        
        if not self._expect(TokenType.LPAREN, "Expected '(' after for"):
            return
        
        # Parse initialization
        self._parse_statement()
        
        # Parse condition
        self._parse_expression()
        
        if not self._expect(TokenType.SEMICOLON, "Expected ';' after for condition"):
            return
        
        # Parse increment
        self._parse_expression()
        
        if not self._expect(TokenType.RPAREN, "Expected ')' after for increment"):
            return
        
        if not self._expect(TokenType.LBRACE, "Expected '{' for for body"):
            return
        
        self._parse_block()
        
        if not self._expect(TokenType.RBRACE, "Expected '}' to end for body"):
            return
    
    def _parse_return_statement(self):
        """Parse a return statement."""
        self._next_token()  # Skip 'return'
        
        if self._current_token().type != TokenType.SEMICOLON:
            self._parse_expression()
        
        if not self._expect(TokenType.SEMICOLON, "Expected ';' after return statement"):
            return
    
    def _parse_variable_declaration(self):
        """Parse a variable declaration."""
        type_token = self._current_token()
        self._next_token()
        
        if not self._expect(TokenType.IDENTIFIER, "Expected variable name"):
            return
        
        if self._current_token().type == TokenType.ASSIGN:
            self._next_token()
            self._parse_expression()
        
        if not self._expect(TokenType.SEMICOLON, "Expected ';' after variable declaration"):
            return
    
    def _parse_assignment_or_function_call(self):
        """Parse an assignment or function call."""
        identifier = self._current_token()
        self._next_token()
        
        if self._current_token().type == TokenType.LPAREN:
            # Function call
            self._next_token()
            self._parse_argument_list()
            
            if not self._expect(TokenType.RPAREN, "Expected ')' after function arguments"):
                return
            
            if not self._expect(TokenType.SEMICOLON, "Expected ';' after function call"):
                return
        else:
            # Assignment
            if not self._expect(TokenType.ASSIGN, "Expected '=' for assignment"):
                return
            
            self._parse_expression()
            
            if not self._expect(TokenType.SEMICOLON, "Expected ';' after assignment"):
                return
    
    def _parse_argument_list(self):
        """Parse a function argument list."""
        if self._current_token().type == TokenType.RPAREN:
            return
        
        while True:
            self._parse_expression()
            
            if self._current_token().type == TokenType.COMMA:
                self._next_token()
                continue
            break
    
    def _parse_expression(self):
        """Parse an expression."""
        self._parse_term()
        
        while self._current_token().type in (TokenType.PLUS, TokenType.MINUS):
            self._next_token()
            self._parse_term()
    
    def _parse_term(self):
        """Parse a term."""
        self._parse_factor()
        
        while self._current_token().type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            self._next_token()
            self._parse_factor()
    
    def _parse_factor(self):
        """Parse a factor."""
        token = self._current_token()
        
        if token.type == TokenType.IDENTIFIER:
            self._next_token()
            
            if self._current_token().type == TokenType.LPAREN:
                # Function call
                self._next_token()
                self._parse_argument_list()
                
                if not self._expect(TokenType.RPAREN, "Expected ')' after function arguments"):
                    return
        elif token.type in (TokenType.INTEGER, TokenType.FLOAT_LITERAL, TokenType.CHAR_LITERAL):
            self._next_token()
        elif token.type == TokenType.LPAREN:
            self._next_token()
            self._parse_expression()
            
            if not self._expect(TokenType.RPAREN, "Expected ')' after expression"):
                return
        else:
            self.errors.append(SyntaxError(
                line=token.line,
                column=token.column,
                message="Invalid expression",
                severity="error",
                suggestion="Expected a valid expression"
            ))
            self._next_token() 