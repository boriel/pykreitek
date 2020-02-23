# -*- coding: utf-8 -*-

from typing import TextIO, Optional

import ast_


class Visitor:
    def __init__(self, output_buffer: TextIO, root: ast_.AST):
        self.root = root
        self.outbuffer = output_buffer
        self.outbuffer.write('#include <stdlib.h>\n\nint main() ')
        self.indent_level = 0

    def visit(self, root: Optional[ast_.AST] = None):
        if root is None:
            root = self.root
        # print('visit_{}'.format(root.__class__.__name__))
        getattr(self, 'visit_{}'.format(root.__class__.__name__))(root)

    def visit_BlockAST(self, ast: ast_.BlockAST):
        self._output('{\n')
        self.indent_level += 1
        for sentence in ast.sentences:
            self.visit(sentence)
        self.indent_level -= 1
        self._output('}')

    def _output(self, s: str):
        self.outbuffer.write(s)

    def _output_line(self, line: str):
        self._output('{}{}\n'.format(' ' * 2 * self.indent_level, line))

    def visit_VarDeclAST(self, ast: ast_.VarDeclAST):
        types = {
            'char': 'wchar_t',
            'int32': 'int32_t',
            'int64': 'int64_t',
            'float': 'double',
        }
        self._output_line('{} {};'.format(types[ast.type_.name], ast.var.var_name))
