"""
Type checking for C code.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from ..lexer.tokenizer import Token, TokenType

@dataclass
class Type:
    name: str
    is_array: bool = False
    array_size: Optional[int] = None
    is_pointer: bool = False

@dataclass
class Variable:
    name: str
    type: Type
    is_initialized: bool = False
    scope_level: int = 0

@dataclass
class Function:
    name: str
    return_type: Type
    parameters: List[Variable]
    is_defined: bool = False

@dataclass
class SemanticError:
    line: int
    column: int
    message: str
    severity: str  # 'error', 'warning', 'info'
    suggestion: str = ''

class TypeChecker:
    def __init__(self):
        self.errors: List[SemanticError] = []
        self.variables: Dict[str, Variable] = {}
        self.functions: Dict[str, Function] = {}
        self.current_scope_level = 0
        self.basic_types = {
            'int': Type('int'),
            'char': Type('char'),
            'float': Type('float'),
            'void': Type('void')
        }
    
    def check_types(self, tokens: List[Token]) -> List[SemanticError]:
        """Check types in the token stream."""
        self.errors.clear()
        self.variables.clear()
        self.functions.clear()
        self.current_scope_level = 0
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type in (TokenType.INT, TokenType.CHAR, TokenType.FLOAT, TokenType.VOID):
                # Function or variable declaration
                if i + 2 < len(tokens) and tokens[i + 2].type == TokenType.LPAREN:
                    i = self._check_function_declaration(tokens, i)
                else:
                    i = self._check_variable_declaration(tokens, i)
            elif token.type == TokenType.IDENTIFIER:
                # Function call or variable usage
                if i + 1 < len(tokens) and tokens[i + 1].type == TokenType.LPAREN:
                    i = self._check_function_call(tokens, i)
                else:
                    i = self._check_variable_usage(tokens, i)
            
            i += 1
        
        return self.errors
    
    def _check_function_declaration(self, tokens: List[Token], start_index: int) -> int:
        """Check a function declaration."""
        return_type = self.basic_types[tokens[start_index].value]
        function_name = tokens[start_index + 1].value
        
        # Check if function is already declared
        if function_name in self.functions:
            self.errors.append(SemanticError(
                line=tokens[start_index].line,
                column=tokens[start_index].column,
                message=f"Function '{function_name}' is already declared",
                severity="error",
                suggestion="Rename the function or remove the duplicate declaration"
            ))
        
        # Parse parameters
        parameters = []
        i = start_index + 3  # Skip return type, name, and '('
        
        while tokens[i].type != TokenType.RPAREN:
            if tokens[i].type in (TokenType.INT, TokenType.CHAR, TokenType.FLOAT):
                param_type = self.basic_types[tokens[i].value]
                param_name = tokens[i + 1].value
                parameters.append(Variable(param_name, param_type, True, self.current_scope_level))
                i += 2
            elif tokens[i].type == TokenType.COMMA:
                i += 1
            else:
                i += 1
        
        # Create function
        self.functions[function_name] = Function(function_name, return_type, parameters, False)
        
        # Check function body
        i += 2  # Skip ')' and '{'
        self.current_scope_level += 1
        
        while tokens[i].type != TokenType.RBRACE:
            if tokens[i].type in (TokenType.INT, TokenType.CHAR, TokenType.FLOAT):
                i = self._check_variable_declaration(tokens, i)
            elif tokens[i].type == TokenType.IDENTIFIER:
                if i + 1 < len(tokens) and tokens[i + 1].type == TokenType.LPAREN:
                    i = self._check_function_call(tokens, i)
                else:
                    i = self._check_variable_usage(tokens, i)
            i += 1
        
        self.current_scope_level -= 1
        return i
    
    def _check_variable_declaration(self, tokens: List[Token], start_index: int) -> int:
        """Check a variable declaration."""
        var_type = self.basic_types[tokens[start_index].value]
        var_name = tokens[start_index + 1].value
        
        # Check if variable is already declared in current scope
        if var_name in self.variables and self.variables[var_name].scope_level == self.current_scope_level:
            self.errors.append(SemanticError(
                line=tokens[start_index].line,
                column=tokens[start_index].column,
                message=f"Variable '{var_name}' is already declared in this scope",
                severity="error",
                suggestion="Rename the variable or remove the duplicate declaration"
            ))
        
        # Check for array declaration
        is_array = False
        array_size = None
        i = start_index + 2
        
        if i < len(tokens) and tokens[i].type == TokenType.LBRACKET:
            is_array = True
            i += 1
            if tokens[i].type == TokenType.INTEGER:
                array_size = int(tokens[i].value)
            i += 2  # Skip ']'
        
        # Check for initialization
        is_initialized = False
        if i < len(tokens) and tokens[i].type == TokenType.ASSIGN:
            is_initialized = True
            i += 1
            i = self._check_expression(tokens, i, var_type)
        
        # Create variable
        var_type.is_array = is_array
        var_type.array_size = array_size
        self.variables[var_name] = Variable(var_name, var_type, is_initialized, self.current_scope_level)
        
        return i
    
    def _check_function_call(self, tokens: List[Token], start_index: int) -> int:
        """Check a function call."""
        function_name = tokens[start_index].value
        
        # Check if function exists
        if function_name not in self.functions:
            self.errors.append(SemanticError(
                line=tokens[start_index].line,
                column=tokens[start_index].column,
                message=f"Function '{function_name}' is not declared",
                severity="error",
                suggestion="Declare the function before using it"
            ))
            return start_index + 1
        
        function = self.functions[function_name]
        i = start_index + 2  # Skip name and '('
        param_index = 0
        
        while tokens[i].type != TokenType.RPAREN:
            if param_index >= len(function.parameters):
                self.errors.append(SemanticError(
                    line=tokens[i].line,
                    column=tokens[i].column,
                    message=f"Too many arguments in call to '{function_name}'",
                    severity="error",
                    suggestion=f"Function expects {len(function.parameters)} arguments"
                ))
                break
            
            param_type = function.parameters[param_index].type
            i = self._check_expression(tokens, i, param_type)
            param_index += 1
            
            if tokens[i].type == TokenType.COMMA:
                i += 1
        
        if param_index < len(function.parameters):
            self.errors.append(SemanticError(
                line=tokens[start_index].line,
                column=tokens[start_index].column,
                message=f"Too few arguments in call to '{function_name}'",
                severity="error",
                suggestion=f"Function expects {len(function.parameters)} arguments"
            ))
        
        return i + 1
    
    def _check_variable_usage(self, tokens: List[Token], start_index: int) -> int:
        """Check variable usage."""
        var_name = tokens[start_index].value
        
        # Check if variable exists
        if var_name not in self.variables:
            self.errors.append(SemanticError(
                line=tokens[start_index].line,
                column=tokens[start_index].column,
                message=f"Variable '{var_name}' is not declared",
                severity="error",
                suggestion="Declare the variable before using it"
            ))
            return start_index + 1
        
        variable = self.variables[var_name]
        i = start_index + 1
        
        # Check array access
        if i < len(tokens) and tokens[i].type == TokenType.LBRACKET:
            if not variable.type.is_array:
                self.errors.append(SemanticError(
                    line=tokens[i].line,
                    column=tokens[i].column,
                    message=f"Variable '{var_name}' is not an array",
                    severity="error",
                    suggestion="Remove array access or declare as array"
                ))
            i += 1
            i = self._check_expression(tokens, i, self.basic_types['int'])
            i += 1  # Skip ']'
        
        # Check assignment
        if i < len(tokens) and tokens[i].type == TokenType.ASSIGN:
            i += 1
            i = self._check_expression(tokens, i, variable.type)
            variable.is_initialized = True
        
        return i
    
    def _check_expression(self, tokens: List[Token], start_index: int, expected_type: Type) -> int:
        """Check an expression."""
        i = start_index
        token = tokens[i]
        
        if token.type == TokenType.IDENTIFIER:
            # Variable or function call
            if i + 1 < len(tokens) and tokens[i + 1].type == TokenType.LPAREN:
                i = self._check_function_call(tokens, i)
            else:
                i = self._check_variable_usage(tokens, i)
        elif token.type in (TokenType.INTEGER, TokenType.FLOAT_LITERAL, TokenType.CHAR_LITERAL):
            # Literal
            if token.type == TokenType.INTEGER and expected_type.name != 'int':
                self.errors.append(SemanticError(
                    line=token.line,
                    column=token.column,
                    message=f"Type mismatch: expected {expected_type.name}, got int",
                    severity="error",
                    suggestion=f"Convert the integer to {expected_type.name}"
                ))
            elif token.type == TokenType.FLOAT_LITERAL and expected_type.name != 'float':
                self.errors.append(SemanticError(
                    line=token.line,
                    column=token.column,
                    message=f"Type mismatch: expected {expected_type.name}, got float",
                    severity="error",
                    suggestion=f"Convert the float to {expected_type.name}"
                ))
            elif token.type == TokenType.CHAR_LITERAL and expected_type.name != 'char':
                self.errors.append(SemanticError(
                    line=token.line,
                    column=token.column,
                    message=f"Type mismatch: expected {expected_type.name}, got char",
                    severity="error",
                    suggestion=f"Convert the char to {expected_type.name}"
                ))
            i += 1
        elif token.type == TokenType.LPAREN:
            # Parenthesized expression
            i += 1
            i = self._check_expression(tokens, i, expected_type)
            i += 1  # Skip ')'
        
        # Check for operators
        while i < len(tokens) and tokens[i].type in (TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE):
            operator = tokens[i]
            i += 1
            i = self._check_expression(tokens, i, expected_type)
        
        return i 