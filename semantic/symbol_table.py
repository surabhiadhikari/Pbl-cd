"""
Symbol table for C code semantic analysis.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .type_checker import Type, Variable, Function

@dataclass
class Symbol:
    name: str
    type: Type
    kind: str  # 'variable', 'function', 'parameter'
    scope_level: int
    is_initialized: bool = False
    is_defined: bool = False

class SymbolTable:
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        self.scope_level = 0
        self.scopes: List[Dict[str, Symbol]] = [{}]
    
    def enter_scope(self):
        """Enter a new scope."""
        self.scope_level += 1
        self.scopes.append({})
    
    def exit_scope(self):
        """Exit the current scope."""
        if self.scope_level > 0:
            self.scope_level -= 1
            self.scopes.pop()
    
    def add_symbol(self, symbol: Symbol) -> bool:
        """Add a symbol to the current scope."""
        if symbol.name in self.scopes[-1]:
            return False
        
        self.scopes[-1][symbol.name] = symbol
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol by name."""
        # Search in current scope first
        if name in self.scopes[-1]:
            return self.scopes[-1][name]
        
        # Search in outer scopes
        for scope in reversed(self.scopes[:-1]):
            if name in scope:
                return scope[name]
        
        return None
    
    def update_symbol(self, name: str, **kwargs) -> bool:
        """Update a symbol's attributes."""
        symbol = self.lookup(name)
        if symbol:
            for key, value in kwargs.items():
                setattr(symbol, key, value)
            return True
        return False
    
    def get_all_symbols(self) -> List[Symbol]:
        """Get all symbols in the table."""
        return list(self.symbols.values())
    
    def get_symbols_in_scope(self, scope_level: int) -> List[Symbol]:
        """Get all symbols in a specific scope."""
        return [symbol for symbol in self.symbols.values() if symbol.scope_level == scope_level]
    
    def clear(self):
        """Clear the symbol table."""
        self.symbols.clear()
        self.scopes = [{}]
        self.scope_level = 0
    
    def add_variable(self, variable: Variable) -> bool:
        """Add a variable to the symbol table."""
        symbol = Symbol(
            name=variable.name,
            type=variable.type,
            kind='variable',
            scope_level=variable.scope_level,
            is_initialized=variable.is_initialized
        )
        return self.add_symbol(symbol)
    
    def add_function(self, function: Function) -> bool:
        """Add a function to the symbol table."""
        symbol = Symbol(
            name=function.name,
            type=function.return_type,
            kind='function',
            scope_level=0,
            is_defined=function.is_defined
        )
        return self.add_symbol(symbol)
    
    def add_parameter(self, variable: Variable) -> bool:
        """Add a parameter to the symbol table."""
        symbol = Symbol(
            name=variable.name,
            type=variable.type,
            kind='parameter',
            scope_level=variable.scope_level,
            is_initialized=True
        )
        return self.add_symbol(symbol)
    
    def get_variables(self) -> List[Symbol]:
        """Get all variables in the symbol table."""
        return [symbol for symbol in self.symbols.values() if symbol.kind == 'variable']
    
    def get_functions(self) -> List[Symbol]:
        """Get all functions in the symbol table."""
        return [symbol for symbol in self.symbols.values() if symbol.kind == 'function']
    
    def get_parameters(self) -> List[Symbol]:
        """Get all parameters in the symbol table."""
        return [symbol for symbol in self.symbols.values() if symbol.kind == 'parameter']
    
    def get_uninitialized_variables(self) -> List[Symbol]:
        """Get all uninitialized variables in the symbol table."""
        return [symbol for symbol in self.symbols.values() 
                if symbol.kind == 'variable' and not symbol.is_initialized]
    
    def get_undefined_functions(self) -> List[Symbol]:
        """Get all undefined functions in the symbol table."""
        return [symbol for symbol in self.symbols.values() 
                if symbol.kind == 'function' and not symbol.is_defined] 