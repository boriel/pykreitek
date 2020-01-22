# -*- coding: utf-8 -*-

import pytest

from lexer import Token, TokenID
import ast_ as ast  # 'ast' name clashes with ast builtin module


def test_raises_wrong_token():
    with pytest.raises(AssertionError) as e:
        ast.SignedIntType(Token(TokenID.I8, 0, 0, 'uint8'))
    assert e.value.args[0] == "TokenID.I8 does not match type name 'uint8'"


def test_i8():
    t = ast.SignedIntType(Token(TokenID.I8, 0, 0, 'int8'))
    assert isinstance(t, ast.SignedIntType)
    assert isinstance(t, ast.IntTypeAST)
    assert isinstance(t, ast.ScalarTypeAST)
    assert isinstance(t, ast.TypeAST)
    assert t.min_val == -128
    assert t.max_val == 127


def test_u8():
    t = ast.UnsignedIntType(Token(TokenID.U8, 0, 0, 'uint8'))
    assert isinstance(t, ast.UnsignedIntType)
    assert isinstance(t, ast.IntTypeAST)
    assert isinstance(t, ast.ScalarTypeAST)
    assert isinstance(t, ast.TypeAST)
    assert t.min_val == 0
    assert t.max_val == 255


def test_i32():
    t = ast.SignedIntType(Token(TokenID.I32, 0, 0, 'int32'))
    assert isinstance(t, ast.SignedIntType)
    assert isinstance(t, ast.IntTypeAST)
    assert isinstance(t, ast.ScalarTypeAST)
    assert isinstance(t, ast.TypeAST)
    assert t.min_val == -2147483648
    assert t.max_val == 2147483647


def test_u32():
    t = ast.UnsignedIntType(Token(TokenID.U32, 0, 0, 'uint32'))
    assert isinstance(t, ast.UnsignedIntType)
    assert isinstance(t, ast.IntTypeAST)
    assert isinstance(t, ast.ScalarTypeAST)
    assert isinstance(t, ast.TypeAST)
    assert t.min_val == 0
    assert t.max_val == (1 << 32) - 1

    
def test_i64():
    t = ast.SignedIntType(Token(TokenID.I64, 0, 0, 'int64'))
    assert isinstance(t, ast.SignedIntType)
    assert isinstance(t, ast.IntTypeAST)
    assert isinstance(t, ast.ScalarTypeAST)
    assert isinstance(t, ast.TypeAST)
    assert t.min_val == -9223372036854775808
    assert t.max_val == 9223372036854775807


def test_u64():
    t = ast.UnsignedIntType(Token(TokenID.U64, 0, 0, 'uint64'))
    assert isinstance(t, ast.UnsignedIntType)
    assert isinstance(t, ast.IntTypeAST)
    assert isinstance(t, ast.ScalarTypeAST)
    assert isinstance(t, ast.TypeAST)
    assert t.min_val == 0
    assert t.max_val == (1 << 64) - 1
