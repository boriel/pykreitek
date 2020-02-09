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


def test_parser_string_literal():
    parser_ = parser.Parser(io.StringIO('  "a string" '))
    ast = parser_.match_string_literal()
    assert ast is not None, "Should parse a String literal"
    assert ast.value == 'a string'
    assert ast.type.name == 'str'


def test_parser_char_literal():
    parser_ = parser.Parser(io.StringIO("  'c' 'q' "))
    ast = parser_.match_char_literal()
    assert ast is not None, "Should parse a Char literal"
    assert ast.value == 'c'
    assert ast.type.name == 'char'

    ast = parser_.match_char_literal()
    assert ast is not None, "Should parse a Char literal"
    assert ast.value == 'q'
    assert ast.type.name == 'char'


def test_parser_primary():
    parser_ = parser.Parser(io.StringIO("  5.e-1  42  'a' \"a string\" "))
    ast = parser_.match_primary()
    assert ast is not None, "Should parse a primary"
    assert ast.value == '5.e-1'
    assert ast.type.name == 'float'

    ast = parser_.match_primary()
    assert ast is not None, "Should parse a primary"
    assert ast.value == '42'
    assert ast.type.name == 'int8'

    ast = parser_.match_primary()
    assert ast is not None, "Should parse a primary"
    assert ast.value == 'a'
    assert ast.type.name == 'char'

    ast = parser_.match_primary()
    assert ast is not None, "Should parse a primary"
    assert ast.value == 'a string'
    assert ast.type.name == 'str'


def test_parser_unary(mocker):
    parser_ = parser.Parser(io.StringIO("  + --1"))
    ast = parser_.match_unary()
    assert ast is not None, "Should parse a unary"
    assert ast.op.value == '+'
    assert ast.primary.op.value == '-'
    assert ast.primary.primary.op.value == '-'
    assert ast.primary.primary.primary.value == '1'

    mocker.patch('log.error')
    parser_ = parser.Parser(io.StringIO("  + --'a'"))
    ast = parser_.match_unary()
    assert ast is None, "Syntax error expected"
    log.error.assert_called_once_with("1: syntax error: unexpected token 'Token<CHAR_LITERAL 1:8 a>'")


def test_parse_unary_with_parenthesis():
    parser_ = parser.Parser(io.StringIO(" -(-1)"))
    ast = parser_.match_unary()
    assert ast is not None, "Should parse a unary"
    assert isinstance(ast, ast_.UnaryExprAST)
    assert ast.op.value == '-'
    assert ast.primary.op.value == '-'
    assert ast.primary.primary.value == '1'


def test_parser_binary():
    parser_ = parser.Parser(io.StringIO("  +1 - 5"))
    ast = parser_.match_binary_or_unary()
    assert ast is not None, "Should parse a binary"
    assert ast.emit() == '(+1 - 5)'

    parser_ = parser.Parser(io.StringIO("1 + 5 * 4"))
    ast = parser_.match_binary_or_unary()
    assert ast is not None, "Should parse a binary"
    assert ast.emit() == '(1 + (5 * 4))'

    parser_ = parser.Parser(io.StringIO("1 + 5 * 4 ** 2"))
    ast = parser_.match_binary_or_unary()
    assert ast is not None, "Should parse a binary"
    assert ast.emit() == '(1 + (5 * (4 ** 2)))'

    parser_ = parser.Parser(io.StringIO("1 + 5 + 4"))
    ast = parser_.match_binary_or_unary()
    assert ast is not None, "Should parse a binary"
    assert ast.emit() == '((1 + 5) + 4)'


def test_parser_arglist():
    parser_ = parser.Parser(io.StringIO(" ((5 - 3), 4, 2 + 3 * -4)"))
    ast = parser_.match_arg_list()
    assert ast is not None, "Should parse an arglist"
    assert isinstance(ast, ast_.ArgListAST)
    assert len(ast.args) == 3
    assert ast.emit() == '((5 - 3), 4, (2 + (3 * -4)))'


def test_id_of_funccall():
    parser_ = parser.Parser(io.StringIO(" f(3, -f(a))"))
    ast = parser_.match_id_or_fcall()
    assert ast is not None, "Should parse an function call"
    assert isinstance(ast, ast_.FunctionCallAST)
    assert len(ast.args.args) == 2
    assert ast.emit() == 'f(3, -f(a))'

    parser_ = parser.Parser(io.StringIO(" f + "))
    ast = parser_.match_id_or_fcall()
    assert ast is not None, "Should parse an Id"
    assert isinstance(ast, ast_.IdAST)
    assert ast.var_name == 'f'


def test_parse_expressions_with_function_calls():
    parser_ = parser.Parser(io.StringIO("  3 + f(4, f(-5, 6 * i ** j)) * (3 + 4) - a"))
    ast = parser_.match_binary_or_unary()
    assert ast is not None, "Should parse an expression with function calls"
    assert ast.emit() == '((3 + (f(4, f(-5, (6 * (i ** j)))) * (3 + 4))) - a)'


def test_parse_assignment():
    parser_ = parser.Parser(io.StringIO(" c = 3 + f(4, f(-5, 6 * i ** j)) * (3 + 4) - a"))
    ast = parser_.match_var_assignment()
    assert ast is not None, "Should parse an assignment"
    assert isinstance(ast, ast_.AssignmentAST)
    assert isinstance(ast.lvalue, ast_.IdAST)
    assert isinstance(ast.rvalue, ast_.BinaryExprAST)
    assert ast.emit() == 'c = ((3 + (f(4, f(-5, (6 * (i ** j)))) * (3 + 4))) - a)'


def test_parse_vardecl(mocker):
    parser_ = parser.Parser(io.StringIO(" var c: int8"))
    ast = parser_.match_var_decl()
    assert ast is not None, "Should parse variable declaration"
    assert isinstance(ast, ast_.VarDeclAST)
    assert isinstance(ast.var, ast_.IdAST)
    assert isinstance(ast.type_, ast_.TypeAST)
    assert ast.var.var_name == 'c'
    assert ast.type_.name == 'int8'

    mocker.patch('log.error')
    parser_ = parser.Parser(io.StringIO(" var c: int8 var c: int8"))
    parser_.match_var_decl()
    ast = parser_.match_var_decl()
    assert ast is None, "Syntax error expected"
    log.error.assert_called_once_with('1: duplicated name "c"')


def test_parse_statement(mocker):
    parser_ = parser.Parser(io.StringIO("""
        var c: int8;
        c = 4;
        f(c);
    """))

    expected = (ast_.VarDeclAST, ast_.AssignmentAST, ast_.ExpressionAST)
    for i in range(3):
        ast = parser_.match_sentence()
        assert ast is not None, "Could not parse sentence {}".format(i + 1)
        assert isinstance(ast, (expected[i]))
