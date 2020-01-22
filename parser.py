# -*- coding: utf-8 -*-

from typing import Union, TextIO, List
from io import StringIO

from lexer import Lexer, Token, TokenID, TOKEN_MAP
import ast_
from symbol_table import SymbolTable


class ParserSyntaxErrorException(BaseException):
    pass


class Parser:
    """ Implements an LL parser
    """
    lookahead: Token

    def __init__(self,
                 input_stream: Union[str, TextIO, StringIO],
                 encoding: str = 'utf-8',
                 output_stream: Union[TextIO, StringIO, None] = None
                 ):
        self.lex = Lexer(
            input_stream=input_stream,
            encoding=encoding
        )
        self.lookahead = self.lex.get_token()
        self.output_stream = output_stream
        self.symbol_table = SymbolTable()
        self._primitive_types = []

        # Populates symbol table
        self._declare_primitive_type()

    def _declare_primitive_type(self):
        """ Declares primitive types
        """
        for type_name in ast_.PRIMITIVE_TYPES:
            if type_name in ('str', 'char'):
                continue  # Numerical types only for the moment

            token = Token(TOKEN_MAP[type_name], 0, 0, type_name)
            if type_name.startswith('u'):  # Unsigned?
                self.symbol_table.declare_symbol(token, ast_.UnsignedIntType(token))
            else:
                self.symbol_table.declare_symbol(token, ast_.SignedIntType(token))


    def parse(self):
        pass

    def error(self, line, msg):
        raise ParserSyntaxErrorException("{}: {}".format(line, msg))

    def error_unexpected_token(self, token: Token):
        self.error(token.line, "syntax error: unexpected token '{}'".format(repr(token)))

    def match(self, tokens: Union[TokenID, List[TokenID]]) -> List[Token]:
        if isinstance(tokens, TokenID):
            tokens = [TokenID]

        result: List[Token] = []
        for tok in tokens:
            if self.lookahead.id_ == tok:
                result.append(self.lookahead)
            else:
                self.error_unexpected_token(self.lookahead)

        return result

    def match_number_literal(self) -> ast_.NumericLiteralAST:
        if self.lookahead == TokenID.INT_LITERAL:
            result = self.match(TokenID.INT_LITERAL)[0]
            for t in PRIMITIVE_INT_TYPES:
                if t.min_val <= result.num_val <= t.max_val:
                    type_ = t
                    break
            else:
                type_ = ast_.TypeFloatAST
        else:
            type_ = ast_.TypeFloatAST



