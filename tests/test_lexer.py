
import io
from main import Lexer, LexException, TokenID, Token


def test_correctly_skips_blanks():
    lex = Lexer(io.StringIO('  \n\r\t'))
    tok = lex.get_token()
    assert tok == Token(TokenID.EOF, 1, 5, '')
