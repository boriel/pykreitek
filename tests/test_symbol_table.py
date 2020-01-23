# -*- coding: utf-8 -*-

from symbol_table import SymbolTable

import pytest


@pytest.fixture()
def symbol_table() -> SymbolTable:
    return SymbolTable()


def test_push_scope(symbol_table):
    assert symbol_table.current_scope == '.'
    symbol_table.push_scope('scope1')
    assert symbol_table.current_scope == '.scope1.'
    symbol_table.push_scope('scope2')
    assert symbol_table.current_scope == '.scope1.scope2.'


def test_push_scope_underflow(symbol_table):
    with pytest.raises(AssertionError) as e:
        symbol_table.pop_scope()
    assert e.value.args[0] == 'Symbol Table scope stack underflow'


def test_pop_scope(symbol_table):
    symbol_table.push_scope('scope1')
    symbol_table.push_scope('scope2')
    symbol_table.pop_scope()
    assert symbol_table.current_scope == '.scope1.'
    symbol_table.pop_scope()
    assert symbol_table.current_scope == '.'

