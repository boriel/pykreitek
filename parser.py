# -*- coding: utf-8 -*-

from typing import Union, TextIO, List, Optional
from io import StringIO

from lexer import Lexer, Token, TokenID, TOKEN_MAP
import ast_
from symbol_table import SymbolTable
import log


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
        self.primitive_types = []

        # Populates symbol table
        self._declare_primitive_type()

    def _declare_primitive_type(self):
        """ Declares primitive types
        """
        for type_name in ast_.PRIMITIVE_TYPES:
            token = Token(TOKEN_MAP[type_name], 0, 0, type_name)

            if type_name in ('str', 'char', 'bool'):
                type_ = ast_.PrimitiveScalarTypeAST(token)
            elif type_name.startswith('u'):  # Unsigned?
                type_ = ast_.UnsignedIntType(token)
            else:
                type_ = ast_.SignedIntType(token)

            self.symbol_table.declare_symbol(token, type_)
            self.primitive_types.append(type_)

    def parse(self):
        pass

    @staticmethod
    def error(line, msg):
        log.error("{}: {}".format(line, msg))

    def error_unexpected_token(self, token: Token = None):
        if token is None:
            token = self.lookahead
        self.error(token.line, "syntax error: unexpected token '{}'".format(repr(token)))

    def match(self, tokens: Union[TokenID, List[TokenID]]) -> List[Token]:
        if isinstance(tokens, TokenID):
            tokens = [tokens]

        result: List[Token] = []
        for tok in tokens:
            if self.lookahead.id_ == tok:
                result.append(self.lookahead)
                self.lookahead = self.lex.get_token()
            else:
                self.error_unexpected_token()

        return result

    def match_number_literal(self) -> Optional[ast_.NumericLiteralAST]:
        if self.lookahead == TokenID.INT_LITERAL:
            token = self.match(TokenID.INT_LITERAL)[0]
            for t in self.primitive_types:
                if not isinstance(t, ast_.IntTypeAST):
                    continue

                if t.min_val <= token.num_val <= t.max_val:
                    type_ = t
                    break
            else:
                type_ = self.symbol_table.resolve_symbol('float')
        elif self.lookahead == TokenID.FLOAT_LITERAL:
            token = self.match(TokenID.FLOAT_LITERAL)[0]
            type_ = self.symbol_table.resolve_symbol('float')
        else:
            self.error_unexpected_token()
            return None

        result = ast_.NumericLiteralAST(token, type_)
        self.lookahead = self.lex.get_token()
        return result

    def match_id(self) -> Optional[ast_.IdAST]:
        token = self.match(TokenID.ID)
        if not token:
            return

        return ast_.IdAST(token[0])

    def match_string_literal(self) -> Optional[ast_.StringLiteral]:
        token = self.match(TokenID.STR_LITERAL)
        if not token:
            return

        result = ast_.StringLiteral(token[0])
        result.type = self.symbol_table.resolve_symbol('str')
        return result
