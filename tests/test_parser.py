# -*- coding: utf-8 -*-

import io
import parser

import ast_
from lexer import Token, TokenID
import log


def test_parser_init():
    parser_ = parser.Parser(io.StringIO(''))
    assert [x.name for x in parser_.primitive_types] == ['int8', 'uint8', 'int32', 'uint32', 'int64',
                                                         'uint64', 'float', 'bool', 'char', 'str']


def test_parser_numeric_literal():
    parser_ = parser.Parser(io.StringIO('  3452  '))
    ast = parser_.match_number_literal()
    assert isinstance(ast.type, ast_.IntTypeAST)
    assert isinstance(ast.token, Token)
    assert ast.token.id_ == TokenID.INT_LITERAL
    assert ast.token.value == '3452'
    assert ast.token.num_val == 3452
    assert ast.type.name == 'int32'


def test_parser_numeric_literal_float():
    parser_ = parser.Parser(io.StringIO('  .3452e2  '))
    ast = parser_.match_number_literal()
    assert isinstance(ast.type, ast_.IntTypeAST)
    assert isinstance(ast.token, Token)
    assert ast.token.id_ == TokenID.FLOAT_LITERAL
    assert ast.token.value == '.3452e2'
    assert ast.token.num_val == 34.52
    assert ast.type.name == 'float'


def test_parser_numeric_error(mocker):
    mocker.patch('log.error')
    parser_ = parser.Parser(io.StringIO('  a '))
    ast = parser_.match_number_literal()
    assert ast is None, "Syntax error expected"
    log.error.assert_called_once_with("1: syntax error: unexpected token 'Token<ID 1:3 a>'")


def test_parser_varname():
    parser_ = parser.Parser(io.StringIO('   _9aa9_ '))
    ast = parser_.match_id()
    assert ast is not None, "Should parse an ID"
    assert ast.var_name == '_9aa9_'
