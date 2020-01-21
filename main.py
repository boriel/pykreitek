# -*- coding: utf-8 -*-


import sys
import argparse
from typing import Union, TextIO, Optional, Callable
from collections import defaultdict
from enum import IntEnum
from io import StringIO


class TokenID(IntEnum):
    EOF = 0
    ID = 5
    INT = 10
    FLOAT = 20

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

        if self.id_ == TokenID.INT:
            self.num_val = int(value)
        elif self.id_ == TokenID.FLOAT:
            self.num_val = float(value)

    def __eq__(self, other):
        return self.id_ == other.id_ and self.value == other.value

    def __repr__(self):
        return 'Token<{} {}:{} {}>'.format(self.id_, self.line, self.col, self.value)


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

    def error_invalid_char(self):
        """ Raises an invalid char exception
        """
        raise LexException("Invalid char '{}' at line {}, column {}".format(self.current_char, self.line, self.col))

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

    def get_token(self) -> Token:
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

            self.error_invalid_char()

        return Token(TokenID.EOF, line=self.line, col=self.col, value='')


if __name__ == '__main__':
    l = Lexer(sys.argv[1])
    c = l.get_next_char()
    while l.current_char:
        c += l.get_next_char()

    print(c)
