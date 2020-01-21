
import io
from lexer import Lexer, LexException, TokenID, Token
import pytest


def test_correctly_skips_blanks():
    lex = Lexer(io.StringIO('  \n\r\t'))
    tok = lex.get_token()
    assert tok.id_ == TokenID.EOF


def test_skip_line_comment():
    lex = Lexer(io.StringIO("""
    // A skipped comment
    """))
    tok = lex.get_token()
    assert tok.id_ == TokenID.EOF

    lex = Lexer(io.StringIO("""
    /// A skipped comment
    """))
    tok = lex.get_token()
    assert tok.id_ == TokenID.EOF

    lex = Lexer(io.StringIO("""
    / // A skipped comment
    """))
    tok = lex.get_token()
    assert tok.id_ == TokenID.DIV

    lex = Lexer(io.StringIO("""
    // A skipped comment
    /"""))
    tok = lex.get_token()
    assert tok.id_ == TokenID.DIV


def test_raises_exception_on_unclosed_block_comment():
    lex = Lexer(io.StringIO("\n/* A skipped comment\n"))
    with pytest.raises(LexException) as exception:
        lex.get_token()

    assert 'Unclosed comment at line 3, column 0' == exception.value.args[0]


def test_parses_block_comment():
    lex = Lexer(io.StringIO("""
       /* A skipped comment
        /*
        */
        /"""))
    tok = lex.get_token()
    assert tok.id_ == TokenID.DIV


def test_raises_unexpected_char():
    lex = Lexer(io.StringIO("!"))
    with pytest.raises(LexException) as exception:
        lex.get_token()

    assert "Invalid char '!' at line 1, column 1" == exception.value.args[0]


def test_get_id():
    lex = Lexer(io.StringIO("    /*  */ _an_identifier"))
    tok = lex.get_token()
    assert tok == Token(TokenID.ID, 0, 0, value='_an_identifier')


def test_unput():
    lex = Lexer(io.StringIO("áéí"))
    lex.get_next_char()
    lex.rewind()
    assert lex.get_next_char() == 'é'


def test_num_is_dot():
    lex = Lexer(io.StringIO("."))
    tok = lex.get_token()
    assert tok == TokenID.DOT

    lex = Lexer(io.StringIO(".e"))
    tok = lex.get_token()
    assert tok == TokenID.DOT

    lex = Lexer(io.StringIO(".e+1"))
    tok = lex.get_token()
    assert tok == TokenID.DOT


def test_num_is_int():
    lex = Lexer(io.StringIO("341e"))
    tok = lex.get_token()
    assert tok == Token(TokenID.INT, 0, 0, '341')

    lex = Lexer(io.StringIO("341 "))
    tok = lex.get_token()
    assert tok == Token(TokenID.INT, 0, 0, '341')

    lex = Lexer(io.StringIO("341e+"))
    tok = lex.get_token()
    assert tok == Token(TokenID.INT, 0, 0, '341')


def test_num_is_float():
    lex = Lexer(io.StringIO("341."))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT, 0, 0, '341.')

    lex = Lexer(io.StringIO("341.5"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT, 0, 0, '341.5')

    lex = Lexer(io.StringIO(".341"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT, 0, 0, '.341')

    lex = Lexer(io.StringIO("341.e"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT, 0, 0, '341.')

    lex = Lexer(io.StringIO("341e1"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT, 0, 0, '341e1')

    lex = Lexer(io.StringIO("341e-1"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT, 0, 0, '341e-1')

    lex = Lexer(io.StringIO("341.5e-1"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT, 0, 0, '341.5e-1')

    lex = Lexer(io.StringIO(".0e-1"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT, 0, 0, '.0e-1')

