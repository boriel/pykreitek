# -*- coding: utf-8 -*-

from typing import Dict, Optional

import ast_
from lexer import Token
import log


class SymbolTable:
    """ Implements a simple symbol table using Dict.
    Scope is given by
    """
    def __init__(self, mangle: str = '.'):
        self.symbols: Dict[str, ast_.TypeAST] = {}
        self.mangle_char = mangle
        self.current_scope = '.'

    def pop_suffix(self, mangled_name: str) -> str:
        return self.mangle_char.join(mangled_name.split(self.mangle_char)[:-1])

    def get_mangled(self, symbol_name: str) -> str:
        assert self.mangle_char not in symbol_name, "Char '{}' not allowed in '{}'".format(
            self.mangle_char, symbol_name
        )
        return self.current_scope + symbol_name

    def push_scope(self, namespace: str):
        self.current_scope = self.get_mangled(namespace) + self.mangle_char

    def pop_scope(self):
        assert self.current_scope != self.mangle_char, "Symbol Table scope stack underflow"
        self.current_scope = self.pop_suffix(self.current_scope[:-1]) + self.mangle_char

    def declare_symbol(self, token: Token, ast_node: ast_.TypeAST) -> bool:
        """ Returns True on success, False on error
        """
        mangled_name = self.current_scope + token.value
        if mangled_name in self.symbols:
            log.error('{}: duplicated name "{}"'.format(token.line, token.value))
            return False

        self.symbols[mangled_name] = ast_node
        return True

    def resolve_symbol(self, symbol_name: str) -> Optional[ast_.TypeAST]:
        scope = self.current_scope
        mangled_name = scope + symbol_name

        while True:
            if mangled_name in self.symbols:
                return self.symbols[mangled_name]

            if scope == self.mangle_char:
                return None  # Not found

            scope = self.pop_suffix(scope[:-1]) + self.mangle_char
            mangled_name = scope + symbol_name
