
import io
from main import Lexer, LexException, TokenID, Token


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
