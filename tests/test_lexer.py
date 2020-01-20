
import io
from main import Lexer, LexException, TokenID, Token
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
