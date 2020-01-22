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


def test_i32():
    t = ast.TypeI32AST(Token(TokenID.I32, 1, 1, 'i32'))
    assert isinstance(t, ast.TypeI32AST)
    assert isinstance(t, ast.SignedIntType)
    assert isinstance(t, ast.IntTypeAST)
    assert isinstance(t, ast.ScalarTypeAST)
    assert isinstance(t, ast.TypeAST)
    assert t.min_val == -2147483648
    assert t.max_val == 2147483647


def test_u32():
    t = ast.TypeU32AST(Token(TokenID.U32, 1, 1, 'u32'))
    assert isinstance(t, ast.TypeU32AST)
    assert isinstance(t, ast.UnsignedIntType)
    assert isinstance(t, ast.IntTypeAST)
    assert isinstance(t, ast.ScalarTypeAST)
    assert isinstance(t, ast.TypeAST)
    assert t.min_val == 0
    assert t.max_val == (1 << 32) - 1

    
def test_i64():
    t = ast.TypeI64AST(Token(TokenID.I64, 1, 1, 'i64'))
    assert isinstance(t, ast.TypeI64AST)
    assert isinstance(t, ast.SignedIntType)
    assert isinstance(t, ast.IntTypeAST)
    assert isinstance(t, ast.ScalarTypeAST)
    assert isinstance(t, ast.TypeAST)
    assert t.min_val == -9223372036854775808
    assert t.max_val == 9223372036854775807


def test_u64():
    t = ast.TypeU64AST(Token(TokenID.U64, 1, 1, 'u64'))
    assert isinstance(t, ast.TypeU64AST)
    assert isinstance(t, ast.UnsignedIntType)
    assert isinstance(t, ast.IntTypeAST)
    assert isinstance(t, ast.ScalarTypeAST)
    assert isinstance(t, ast.TypeAST)
    assert t.min_val == 0
    assert t.max_val == (1 << 64) - 1
