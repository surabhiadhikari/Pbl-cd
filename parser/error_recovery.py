"""
Error recovery strategies for C code parsing.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from ..lexer.tokenizer import Token, TokenType
from .syntax_analyzer import SyntaxError

@dataclass
class RecoveryStrategy:
    name: str
    description: str
    severity: str  # 'error', 'warning', 'info'
    suggestion: str

class ErrorRecovery:
    def __init__(self):
        self.strategies: Dict[str, RecoveryStrategy] = {
            'missing_semicolon': RecoveryStrategy(
                name="Missing Semicolon",
                description="Add missing semicolon at the end of the statement",
                severity="error",
                suggestion="Add a semicolon (;) at the end of the statement"
            ),
            'missing_brace': RecoveryStrategy(
                name="Missing Brace",
                description="Add missing brace to complete the block",
                severity="error",
                suggestion="Add the missing brace to complete the block"
            ),
            'missing_parenthesis': RecoveryStrategy(
                name="Missing Parenthesis",
                description="Add missing parenthesis to complete the expression",
                severity="error",
                suggestion="Add the missing parenthesis to complete the expression"
            ),
            'invalid_identifier': RecoveryStrategy(
                name="Invalid Identifier",
                description="Fix invalid identifier name",
                severity="error",
                suggestion="Use only letters, numbers, and underscores in identifier names"
            ),
            'type_mismatch': RecoveryStrategy(
                name="Type Mismatch",
                description="Fix type mismatch in assignment or function call",
                severity="error",
                suggestion="Ensure the types match in the assignment or function call"
            )
        }
    
    def recover_from_error(self, error: SyntaxError, tokens: List[Token], current_index: int) -> Optional[int]:
        """Attempt to recover from a syntax error and return the new token index."""
        if "semicolon" in error.message.lower():
            return self._recover_missing_semicolon(tokens, current_index)
        elif "brace" in error.message.lower():
            return self._recover_missing_brace(tokens, current_index)
        elif "parenthesis" in error.message.lower():
            return self._recover_missing_parenthesis(tokens, current_index)
        elif "identifier" in error.message.lower():
            return self._recover_invalid_identifier(tokens, current_index)
        elif "type" in error.message.lower():
            return self._recover_type_mismatch(tokens, current_index)
        
        return None
    
    def _recover_missing_semicolon(self, tokens: List[Token], current_index: int) -> Optional[int]:
        """Recover from a missing semicolon error."""
        # Look ahead for the next statement
        for i in range(current_index + 1, len(tokens)):
            token = tokens[i]
            if token.type in (TokenType.IF, TokenType.WHILE, TokenType.FOR, TokenType.RETURN):
                return i
            elif token.type == TokenType.SEMICOLON:
                return i + 1
        return None
    
    def _recover_missing_brace(self, tokens: List[Token], current_index: int) -> Optional[int]:
        """Recover from a missing brace error."""
        # Look ahead for the next closing brace
        brace_count = 1
        for i in range(current_index + 1, len(tokens)):
            token = tokens[i]
            if token.type == TokenType.LBRACE:
                brace_count += 1
            elif token.type == TokenType.RBRACE:
                brace_count -= 1
                if brace_count == 0:
                    return i + 1
        return None
    
    def _recover_missing_parenthesis(self, tokens: List[Token], current_index: int) -> Optional[int]:
        """Recover from a missing parenthesis error."""
        # Look ahead for the next closing parenthesis
        paren_count = 1
        for i in range(current_index + 1, len(tokens)):
            token = tokens[i]
            if token.type == TokenType.LPAREN:
                paren_count += 1
            elif token.type == TokenType.RPAREN:
                paren_count -= 1
                if paren_count == 0:
                    return i + 1
        return None
    
    def _recover_invalid_identifier(self, tokens: List[Token], current_index: int) -> Optional[int]:
        """Recover from an invalid identifier error."""
        # Skip the invalid identifier and look for the next valid token
        for i in range(current_index + 1, len(tokens)):
            token = tokens[i]
            if token.type in (TokenType.SEMICOLON, TokenType.COMMA, TokenType.RPAREN):
                return i
        return None
    
    def _recover_type_mismatch(self, tokens: List[Token], current_index: int) -> Optional[int]:
        """Recover from a type mismatch error."""
        # Skip the current expression and look for the next statement
        for i in range(current_index + 1, len(tokens)):
            token = tokens[i]
            if token.type == TokenType.SEMICOLON:
                return i + 1
            elif token.type in (TokenType.IF, TokenType.WHILE, TokenType.FOR, TokenType.RETURN):
                return i
        return None
    
    def get_recovery_strategy(self, error: SyntaxError) -> Optional[RecoveryStrategy]:
        """Get the appropriate recovery strategy for an error."""
        if "semicolon" in error.message.lower():
            return self.strategies['missing_semicolon']
        elif "brace" in error.message.lower():
            return self.strategies['missing_brace']
        elif "parenthesis" in error.message.lower():
            return self.strategies['missing_parenthesis']
        elif "identifier" in error.message.lower():
            return self.strategies['invalid_identifier']
        elif "type" in error.message.lower():
            return self.strategies['type_mismatch']
        
        return None 