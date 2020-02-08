# -*- coding: utf-8 -*-

import pytest

from symbol_table import SymbolTable
from lexer import Token, TokenID
import ast_
import log


@pytest.fixture()
def symbol_table() -> SymbolTable:
    return SymbolTable()


def test_push_scope(symbol_table: SymbolTable):
    assert symbol_table.current_scope == '.'
    symbol_table.push_scope('scope1')
    assert symbol_table.current_scope == '.scope1.'
    symbol_table.push_scope('scope2')
    assert symbol_table.current_scope == '.scope1.scope2.'


def test_push_scope_underflow(symbol_table: SymbolTable):
    with pytest.raises(AssertionError) as e:
        symbol_table.pop_scope()
    assert e.value.args[0] == 'Symbol Table scope stack underflow'


def test_pop_scope(symbol_table: SymbolTable):
    symbol_table.push_scope('scope1')
    symbol_table.push_scope('scope2')
    symbol_table.pop_scope()
    assert symbol_table.current_scope == '.scope1.'
    symbol_table.pop_scope()
    assert symbol_table.current_scope == '.'


def test_duplicated_name(symbol_table: SymbolTable, mocker):
    mocker.patch('log.error')
    token = Token(TokenID.ID, 1, 1, 'int8')
    symbol_table.declare_symbol(token, ast_.SignedIntType(token))
    log.error.assert_not_called()
    symbol_table.declare_symbol(token, ast_.SignedIntType(token))
    log.error.assert_called_once_with('1: duplicated name "int8"')


def test_resolve_symbol(symbol_table: SymbolTable):
    token = Token(TokenID.ID, 0, 0, 'char')
    char_type = ast_.PrimitiveScalarTypeAST(token, 'char')
    symbol_table.declare_symbol(token, char_type)
    assert symbol_table.resolve_symbol('char') == char_type

    symbol_table.push_scope('local')
    token = Token(TokenID.ID, 0, 0, 'str')
    str_type = ast_.PrimitiveScalarTypeAST(token, 'str')
    symbol_table.declare_symbol(token, str_type)
    assert symbol_table.resolve_symbol('str') == str_type
    assert symbol_table.resolve_symbol('char') == char_type
    assert not symbol_table.resolve_symbol('unknown')
