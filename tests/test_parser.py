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
    parser_ = parser.Parser(io.StringIO(" c = 3 + f(4, f(-5, 6 * i ** j)) * (3 + 4) - a;"))
    ast = parser_.match_var_assignment()
    assert ast is not None, "Should parse an assignment"
    assert isinstance(ast, ast_.AssignmentAST)
    assert isinstance(ast.lvalue, ast_.IdAST)
    assert isinstance(ast.rvalue, ast_.BinaryExprAST)
    assert ast.emit() == 'c = ((3 + (f(4, f(-5, (6 * (i ** j)))) * (3 + 4))) - a)'


def test_parse_vardecl(mocker):
    parser_ = parser.Parser(io.StringIO(" var c: int8;"))
    ast = parser_.match_var_decl()
    assert ast is not None, "Should parse variable declaration"
    assert isinstance(ast, ast_.VarDeclAST)
    assert isinstance(ast.var, ast_.IdAST)
    assert isinstance(ast.type_, ast_.TypeAST)
    assert ast.var.var_name == 'c'
    assert ast.type_.name == 'int8'

    mocker.patch('log.error')
    parser_ = parser.Parser(io.StringIO(" var c: int8; var c: int8;"))
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

    mocker.patch('log.error')
    parser_ = parser.Parser(io.StringIO("""
        var c: int8;
        c = 4
        f(c);
    """))
    parser_.match_sentence()
    ast = parser_.match_sentence()
    assert ast is None, "Syntax error expected"
    log.error.assert_called_once_with("4: syntax error: unexpected token 'Token<ID 4:9 f>'")


def test_parse_block():
    parser_ = parser.Parser(io.StringIO("""
        {
            var c: int8;
            c = 4;
            {
                var c: int8;
                c = 4;
                f(c);
            }
            f(c);
        }
    """))
    ast = parser_.match_block()
    assert ast is not None, "Should parse scope"
    assert isinstance(ast, ast_.BlockAST)
    assert len(ast.sentences) == 4
    expected = (ast_.VarDeclAST, ast_.AssignmentAST, ast_.BlockAST, ast_.FunctionCallAST)
    for i in range(4):
        assert isinstance(ast.sentences[i], (expected[i])), "Failed parsing sentence {}".format(i)

    assert ast.emit() == '{\nint8 c;\nc = 4;\n{\nint8 c;\nc = 4;\nf(c);\n};\nf(c);\n}'

    assert len(ast.sentences[2].sentences) == 3
    expected = (ast_.VarDeclAST, ast_.AssignmentAST, ast_.FunctionCallAST)
    for i in range(3):
        assert isinstance(ast.sentences[2].sentences[i], (expected[i])), \
            "Failed parsing sentence {} in nested block".format(i)


def test_parse_param_list():
    parser_ = parser.Parser(io.StringIO("(a: int8, c: int32, d: str)"))
    ast = parser_.match_param_list()
    assert ast is not None, "Should parse param list"
    assert isinstance(ast, ast_.ParamListAST)
    assert len(ast.parameters) == 3
    assert ('a', 'c', 'd') == tuple(x.var.var_name for x in ast.parameters)


def test_parse_function(mocker):
    parser_ = parser.Parser(io.StringIO("""
        fn myfunc(a: int8, c: int32, d: str): char {
            c = c + 1;
            var de: str;
            de = d + " ";
        }
        """))
    ast = parser_.match_funcdecl()
    assert ast is not None, "Should parse function declaration"
    assert ast.emit() == 'char myfunc(int8 a, int32 c, str d) {\nc = (c + 1);\nstr de;\nde = (d + " ");\n}'

    mocker.patch('log.error')
    parser_ = parser.Parser(io.StringIO("""
        fn myfunc(a: int8, c: int32, d: str): char {
            c = c + 1;
            var c: str;
            de = d + " ";
        }
        """))
    ast = parser_.match_funcdecl()
    assert ast is None, "Should not parse function declaration with duplicated var name"
    log.error.assert_called_once_with('4: duplicated name "c"')


def test_parse_if():
    parser_ = parser.Parser(io.StringIO("""
        if a < 10 {
           if b + 1 == 5 {
              c = 0;
           }
        } else {
            if a * 4 {
                f(a) + 1;
            }
        }
    """))
    ast = parser_.match_if_sentence()
    assert ast is not None, "Should parse if"

    parser_ = parser.Parser(io.StringIO("""
        if a < 10
           if b + 1 == 5 {
              c = 0;
           }
        else {
            if a * 4 {
                f(a) + 1;
            }
        }
    """))
    ast = parser_.match_if_sentence()
    assert ast is not None, "Should parse if"
    assert ast.emit() == "if ((a < 10)) {\nif (((b + 1) == 5)) {\n{\nc = 0;\n}\n} else" \
                         " {\n{\nif ((a * 4)) {\n{\n(f(a) + 1);\n}\n};\n}\n}\n}"

