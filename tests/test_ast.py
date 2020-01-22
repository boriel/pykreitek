# -*- coding: utf-8 -*-

from lexer import Token, TokenID
import ast_ as ast  # 'ast' name clashes with ast builtin module


def test_i8():
    t = ast.TypeI8AST(Token(TokenID.I8, 1, 1, 'i8'))
    assert isinstance(t, ast.TypeI8AST)
    assert isinstance(t, ast.SignedIntType)
    assert isinstance(t, ast.IntTypeAST)
    assert isinstance(t, ast.ScalarTypeAST)
    assert isinstance(t, ast.TypeAST)
    assert t.min_val == -128
    assert t.max_val == 127


def test_u8():
    t = ast.TypeU8AST(Token(TokenID.U8, 1, 1, 'u8'))
    assert isinstance(t, ast.TypeU8AST)
    assert isinstance(t, ast.UnsignedIntType)
    assert isinstance(t, ast.IntTypeAST)
    assert isinstance(t, ast.ScalarTypeAST)
    assert isinstance(t, ast.TypeAST)
    assert t.min_val == 0
    assert t.max_val == 255

