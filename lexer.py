# -*- coding: utf-8 -*-


import sys
from typing import Union, TextIO
from enum import IntEnum
from io import StringIO, SEEK_SET


class TokenID(IntEnum):
    def __repr__(self):
        return self.name

    EOF = 0
    ID = 5
    INT_LITERAL = 10
    FLOAT_LITERAL = 20
    STR_LITERAL = 25
    CHAR_LITERAL = 27

    ASSIGN = 30
    PLUS = 40
    MINUS = 50
    MUL = 60
    DIV = 70
    MOD = 80

    A_PLUS = 90
    A_MINUS = 100
    A_MUL = 110
    A_DIV = 120
    A_MOD = 130

    EQ = 150
    LT = 155
    LE = 160
    GT = 165
    GE = 170
    NE = 175

    DOT = 200
    COMMA = 205
    SC = 210
    CO = 215
    LP = 220
    RP = 230
    LBR = 240
    RBR = 250
    LSBR = 260
    RSBR = 270

    FN = 1000
    MUT = 1010
    IF = 1020
    ELSE = 1030
    RETURN = 1040
    WHILE = 1145

    I8 = 1050
    U8 = 1060
    I32 = 1070
    U32 = 1080
    I64 = 1090
    U64 = 1100
    FLOAT = 1120
    CHAR = 1130
    STR = 1140
    BOOL = 1150


TOKEN_MAP = {
    '+': TokenID.PLUS,
    '+=': TokenID.A_PLUS,
    '-': TokenID.MINUS,
    '-=': TokenID.A_MINUS,
    '*': TokenID.MUL,
    '*=': TokenID.A_MUL,
    '%': TokenID.MOD,
    '%=': TokenID.A_MOD,
    '=': TokenID.ASSIGN,
    '==': TokenID.EQ,
    '!=': TokenID.NE,
    '<': TokenID.LT,
    '<=': TokenID.LE,
    '>': TokenID.GT,
    '>=': TokenID.GE,

    '.': TokenID.DOT,
    ',': TokenID.COMMA,
    ':': TokenID.CO,
    ';': TokenID.SC,

    '{': TokenID.LBR,
    '}': TokenID.RBR,
    '(': TokenID.LP,
    ')': TokenID.RP,
    '[': TokenID.LSBR,
    ']': TokenID.RSBR,

    "fn": TokenID.FN,
    "mut": TokenID.MUT,
    "if": TokenID.IF,
    "else": TokenID.ELSE,
    "return": TokenID.RETURN,
    "while": TokenID.WHILE,

    "char": TokenID.CHAR,
    "str": TokenID.STR,
    "int8": TokenID.I8,
    "uint8": TokenID.U8,
    "int32": TokenID.I32,
    "uint32": TokenID.U32,
    "int64": TokenID.I64,
    "uint64": TokenID.U64,
    "float": TokenID.FLOAT,
    "bool": TokenID.BOOL
}


class Token:
    id_: int
    col: int
    line: int
    value: str
    num_val: Union[int, float]

    def __init__(self, id_: int, line: int, col: int, value: str):
        self.id_ = id_
        self.line = line
        self.col = col
        self.value = value

        if self.id_ == TokenID.INT_LITERAL:
            self.num_val = int(value)
        elif self.id_ == TokenID.FLOAT_LITERAL:
            self.num_val = float(value)

    def __eq__(self, other):
        if isinstance(other, TokenID):
            return self.id_ == other

        return self.id_ == other.id_ and self.value == other.value

    def __repr__(self):
        return 'Token<{} {}:{} {}>'.format(repr(self.id_), self.line, self.col, self.value)


class LexException(BaseException):
    pass


class Lexer:
    """ Implements a simple utf-8 Lexer
    """
    _stream: TextIO
    current_char: str = ''
    col: int
    line: int
    _token_counter: int
    text: str

    def __init__(self,
                 input_stream: Union[str, TextIO, StringIO],
                 encoding: str = 'utf-8',
                 skip_chars: str = ' \n\r\t'):
        if isinstance(input_stream, (TextIO, StringIO)):
            self._stream = input_stream
        else:
            self._stream = open(input_stream, 'rt', encoding=encoding)

        self.line = 1
        self.col = 0
        self._skip_chars = skip_chars
        _token_counter = 1
        self.current_char = self.get_next_char()

    def get_next_char(self) -> str:
        if self.current_char == '\n':
            self.line += 1
            self.col = 0

        self.current_char = self._stream.read(1)
        if self.current_char:
            self.col += 1

        return self.current_char

    def error_invalid_char(self, line=None, col=None, char=None):
        """ Raises an invalid char exception
        """
        if char is None:
            char = self.current_char
        if col is None:
            col = self.col
        if line is None:
            line = self.line

        raise LexException("Invalid char '{}' at line {}, column {}".format(char, line, col))

    def skip_to_eol(self):
        while self.current_char and self.current_char != '\n':
            self.get_next_char()

    def skip_until_close_comment(self):
        """ Skips until finding a closing */ or EOF (in which case raises an error)
        """
        while self.current_char:
            if self.current_char == '*':
                self.get_next_char()

                if self.current_char == '/':
                    self.get_next_char()
                    return

                if self.current_char == '*':
                    continue

            self.get_next_char()

        raise LexException("Unclosed comment at line {}, column {}".format(self.line, self.col))

    def get_identifier(self) -> Token:
        initial_col = self.col
        while self.current_char.isalnum() or self.current_char == '_':
            self.text += self.current_char
            self.get_next_char()

        return Token(TOKEN_MAP.get(self.text, TokenID.ID), line=self.line, col=initial_col, value=self.text)

    def get_number(self) -> Token:
        """ Returns either an integer or a float
        """
        initial_col = self.col
        while self.current_char.isnumeric():
            self.text += self.current_char
            self.get_next_char()

        if self.current_char not in '.eE':
            return Token(TokenID.INT_LITERAL, line=self.line, col=initial_col, value=self.text)

        if self.current_char == '.':
            self.text += '.'
            self.get_next_char()

            while self.current_char.isnumeric():
                self.text += self.current_char
                self.get_next_char()

            if self.text == '.':
                return Token(TokenID.DOT, line=self.line, col=self.col, value='.')

        if self.current_char in 'eE':
            # Here we have either an integer, or a float number
            self.text += 'e'
            self.get_next_char()

            if self.current_char in '-+':
                self.text += self.current_char
                self.get_next_char()

            while self.current_char.isnumeric():
                self.text += self.current_char
                self.get_next_char()

            if self.text[-1] in '+-':
                # No numbers after the NUM. i.e. 2e+. Means a syntax error probably
                self.rewind()
                self.text = self.text[:-1]  # Remove trailing e

            if self.text[-1] == 'e':
                self.rewind()
                self.text = self.text[:-1]  # Remove trailing e

        if 'e' in self.text or '.' in self.text:
            return Token(TokenID.FLOAT_LITERAL, line=self.line, col=initial_col, value=self.text)

        return Token(TokenID.INT_LITERAL, line=self.line, col=initial_col, value=self.text)

    def get_oper(self) -> Token:
        ini_col = self.col

        self.text = self.current_char
        self.get_next_char()

        if self.current_char == '=':
            self.text += '='
            self.get_next_char()

        if self.text not in TOKEN_MAP:
            self.error_invalid_char(col=ini_col, char=self.text)

        return Token(TOKEN_MAP[self.text], self.line, ini_col, self.text)

    def rewind(self, n=1):
        """ Rewinds n characters back. Defaults rewind 1 char
        """
        self._stream.seek(max(0, self._stream.tell() - n), SEEK_SET)

    def get_string(self) -> Token:
        """ Catches a string literal
        """
        ini_col = self.col
        self.text = ''

        while True:
            self.get_next_char()
            if self.current_char == '\\':
                self.get_next_char()
                self.text += self.current_char
                continue
            elif self.current_char == '"':
                self.get_next_char()
                break
            elif self.current_char == '' or self.current_char == '\n':
                raise LexException('Unclosed string literal at line {}, column {}'.format(self.line, ini_col))

            self.text += self.current_char

        return Token(TokenID.STR_LITERAL, line=self.line, col=ini_col, value=self.text)

    def get_char(self) -> Token:
        """ Scans a quoted char
        """
        char = self.get_next_char()
        col = self.col
        if self.get_next_char() != "'":
            raise LexException("Unclosed char literal. Expected ' at line {}, column {}".format(self.line, self.col))

        return Token(TokenID.CHAR_LITERAL, self.line, col, char)

    def get_token(self) -> Token:
        self.text = ''

        while self.current_char:
            if self.current_char in self._skip_chars:
                self.get_next_char()
                continue

            if self.current_char == '/':
                self.get_next_char()

                if self.current_char == '/':  # Line comment?
                    self.skip_to_eol()
                    continue

                if self.current_char == '*':  # Block comment?
                    self.skip_until_close_comment()
                    continue

                if self.current_char == '=':
                    result = Token(TokenID.A_DIV, self.line, self.col - 1, value='/=')
                    self.get_next_char()
                    return result

                return Token(TokenID.DIV, self.line, self.col - 1, value='/')

            if self.current_char.isalpha() or self.current_char == '_':
                return self.get_identifier()

            if self.current_char.isnumeric() or self.current_char == '.':
                return self.get_number()

            if self.current_char in '+-*%<>=!':
                return self.get_oper()

            if self.current_char in '.,:;[](){}':
                self.text = self.current_char
                self.get_next_char()
                return Token(TOKEN_MAP[self.text], self.line, self.col, self.text)

            if self.current_char == '"':
                return self.get_string()

            if self.current_char == "'":
                return self.get_char()

            self.error_invalid_char()

        return Token(TokenID.EOF, line=self.line, col=self.col, value='')


if __name__ == '__main__':
    l = Lexer(sys.argv[1])
    c = l.get_next_char()
    while l.current_char:
        c += l.get_next_char()

    print(c)
