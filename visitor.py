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
            self._indent()
            self.visit(sentence)
            self._output_line('')
        self.indent_level -= 1
        self._output('}')

    def _output(self, s: str):
        self.outbuffer.write(s)

    def _indent(self):
        self._output('{}'.format(' ' * 2 * self.indent_level))

    def _output_line(self, line: str):
        self._output('{}\n'.format(line))

    def visit_VarDeclAST(self, ast: ast_.VarDeclAST):
        types = {
            'char': 'wchar_t',
            'int32': 'int32_t',
            'int64': 'int64_t',
            'float': 'double',
        }
        self._output('{} {};'.format(types[ast.type_.name], ast.var.var_name))

    def visit_NumericLiteralAST(self, ast: ast_.NumericLiteralAST):
        self._output('{}'.format(ast.value))

    def visit_IdAST(self, ast: ast_.IdAST):
        self._output('{}'.format(ast.var_name))

    def visit_AssignmentAST(self, ast: ast_.AssignmentAST):
        self._output('{} = '.format(ast.lvalue.var_name))
        self.visit(ast.rvalue)
        self._output(';')

    def visit_BinaryExprAST(self, ast: ast_.BinaryExprAST):
        self._output('(')
        self.visit(ast.left)
        self._output(' {} '.format(ast.op.value))
        self.visit(ast.right)
        self._output(')')
