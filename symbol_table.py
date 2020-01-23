# -*- coding: utf-8 -*-

from typing import Dict

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

    def push_scope(self, namespace: str):
        self.current_scope += namespace + self.mangle_char

    def pop_scope(self):
        assert self.current_scope != self.mangle_char, "Symbol Table scope stack underflow"
        self.current_scope = self.mangle_char.join(self.current_scope.split(self.mangle_char)[:-2]) + \
            self.mangle_char

    def declare_symbol(self, token: Token, ast_node: ast_.TypeAST):
        mangled_name = self.current_scope + token.value
        if mangled_name in self.symbols:
            log.error('{}: duplicated name "{}"'.format(token.line, token.value))

        self.symbols[mangled_name] = ast_node
