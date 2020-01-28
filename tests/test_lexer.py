
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
    assert tok == Token(TokenID.INT_LITERAL, 0, 0, '341')

    lex = Lexer(io.StringIO("341 "))
    tok = lex.get_token()
    assert tok == Token(TokenID.INT_LITERAL, 0, 0, '341')

    lex = Lexer(io.StringIO("341e+"))
    tok = lex.get_token()
    assert tok == Token(TokenID.INT_LITERAL, 0, 0, '341')


def test_num_is_float():
    lex = Lexer(io.StringIO("341."))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT_LITERAL, 0, 0, '341.')

    lex = Lexer(io.StringIO("341.5"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT_LITERAL, 0, 0, '341.5')

    lex = Lexer(io.StringIO(".341"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT_LITERAL, 0, 0, '.341')

    lex = Lexer(io.StringIO("341.e"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT_LITERAL, 0, 0, '341.')

    lex = Lexer(io.StringIO("341e1"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT_LITERAL, 0, 0, '341e1')

    lex = Lexer(io.StringIO("341e-1"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT_LITERAL, 0, 0, '341e-1')

    lex = Lexer(io.StringIO("341.5e-1"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT_LITERAL, 0, 0, '341.5e-1')

    lex = Lexer(io.StringIO(".0e-1"))
    tok = lex.get_token()
    assert tok == Token(TokenID.FLOAT_LITERAL, 0, 0, '.0e-1')


def test_operators():
    lex = Lexer(io.StringIO("!= == = + += - -= * *= / /= % %= < <= > >="))
    for tok_id in [
        TokenID.NE,
        TokenID.EQ,
        TokenID.ASSIGN,
        TokenID.PLUS,
        TokenID.A_PLUS,
        TokenID.MINUS,
        TokenID.A_MINUS,
        TokenID.MUL,
        TokenID.A_MUL,
        TokenID.DIV,
        TokenID.A_DIV,
        TokenID.MOD,
        TokenID.A_MOD,
        TokenID.LT,
        TokenID.LE,
        TokenID.GT,
        TokenID.GE,
        TokenID.EOF
    ]:
        tok = lex.get_token()
        assert tok == tok_id


def test_various():
    lex = Lexer(io.StringIO("( ) [ ] { } ., ; :"))
    for tok_id in [
        TokenID.LP,
        TokenID.RP,
        TokenID.LSBR,
        TokenID.RSBR,
        TokenID.LBR,
        TokenID.RBR,
        TokenID.DOT,
        TokenID.COMMA,
        TokenID.SC,
        TokenID.CO,
        TokenID.EOF
    ]:
        tok = lex.get_token()
        assert tok == tok_id


def test_reserved_words():
    lex = Lexer(io.StringIO("fn mut if else return while char str int8 uint8 int32 uint32 int64 uint64 float"))

    for tok_id in [
        TokenID.FN,
        TokenID.MUT,
        TokenID.IF,
        TokenID.ELSE,
        TokenID.RETURN,
        TokenID.WHILE,
        TokenID.CHAR,
        TokenID.STR,
        TokenID.I8,
        TokenID.U8,
        TokenID.I32,
        TokenID.U32,
        TokenID.I64,
        TokenID.U64,
        TokenID.FLOAT,
        TokenID.EOF
    ]:
        tok = lex.get_token()
        assert tok == tok_id


def test_string_literal():
    lex = Lexer(io.StringIO(r'   "  \"string\"  "'))
    tok = lex.get_token()
    assert tok == Token(TokenID.STR_LITERAL, 0, 0, '  "string"  ')

    lex = Lexer(io.StringIO(r'   "  \"string\"  "  "another string" '))
    tok = lex.get_token()
    assert tok == Token(TokenID.STR_LITERAL, 0, 0, '  "string"  ')
    tok = lex.get_token()
    assert tok == Token(TokenID.STR_LITERAL, 0, 0, 'another string')

    with pytest.raises(LexException) as ex:
        lex = Lexer(io.StringIO(r'   "  \"string\" '))
        lex.get_token()
    assert 'Unclosed string literal at line 1, column 4' == ex.value.args[0]

    with pytest.raises(LexException) as ex:
        lex = Lexer(io.StringIO(r'   "  \"string\" \n'))
        lex.get_token()
    assert 'Unclosed string literal at line 1, column 4' == ex.value.args[0]


def test_char_literal():
    lex = Lexer(io.StringIO(" 'ñ' "))
    assert lex.get_token() == Token(TokenID.CHAR_LITERAL, 1, 3, 'ñ')

    lex = Lexer(io.StringIO(" 'a"))
    with pytest.raises(LexException) as ex:
        lex.get_token()
    assert "Unclosed char literal. Expected ' at line 1, column 3" == ex.value.args[0]

    lex = Lexer(io.StringIO(" '' "))
    with pytest.raises(LexException) as ex:
        lex.get_token()
    assert "Empty char value not allowed" == ex.value.args[0]

    lex = Lexer(io.StringIO(" 'ñ' 'a' "))
    assert lex.get_token() == Token(TokenID.CHAR_LITERAL, 1, 3, 'ñ')
    assert lex.get_token() == Token(TokenID.CHAR_LITERAL, 1, 7, 'a')
