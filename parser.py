# -*- coding: utf-8 -*-

from typing import Union, TextIO, List, Optional
from io import StringIO

from lexer import Lexer, Token, TokenID, TOKEN_MAP
import ast_
from symbol_table import SymbolTable
import log


class ParserSyntaxErrorException(BaseException):
    pass


# Binary operator precedence (higher value, higher priority)
OPERATOR_PRECEDENCE = {
    '>': 10,
    '<': 10,
    '==': 10,
    '<=': 10,
    '>=': 10,
    '!=': 10,
    '+': 20,
    '-': 20,
    '*': 30,
    '/': 30,
    '%': 30,
    '**': 40,
}


class Parser:
    """ Implements an LL parser
    """
    lookahead: Token

    def __init__(self,
                 input_stream: Union[str, TextIO, StringIO],
                 encoding: str = 'utf-8'
                 ):
        self.lex = Lexer(
            input_stream=input_stream,
            encoding=encoding
        )
        self.lookahead = self.lex.get_token()
        self.symbol_table = SymbolTable()
        self.primitive_types = []
        self.scope_counter = 0

        # Populates symbol table
        self._declare_primitive_types()

    def peek(self, n: int = 0) -> Token:
        """ Looks ahead n tokens. 0 = current lookahead
        """
        assert n >= 0
        return self.lex.lookahead(n) if n > 0 else self.lookahead

    def _declare_primitive_types(self):
        """ Declares primitive types
        """
        for type_name in ast_.PRIMITIVE_TYPES:
            token = Token(TokenID.ID, 0, 0, type_name)

            if type_name in ('str', 'char', 'bool'):
                type_ = ast_.PrimitiveScalarTypeAST(token)
            elif type_name.startswith('u'):  # Unsigned?
                type_ = ast_.UnsignedIntType(token)
            else:
                type_ = ast_.SignedIntType(token)

            self.symbol_table.declare_symbol(token, type_)
            self.primitive_types.append(type_)

    def start_scope(self, id_: str = None):
        """ Starts a new scope with an associated ID (string) which will
        be used, for example, as a mangle prefix for symbols defined within
        it. If no ID is specified, an random unique one will be created.
        """
        if id_ is None:
            id_ = 'S{}'.format(self.scope_counter)
            self.scope_counter += 1

        self.symbol_table.push_scope(id_)

    def end_scope(self):
        """ Closes a scope
        """
        self.symbol_table.pop_scope()

    @property
    def current_scope(self) -> str:
        """ Returns current scope in use
        """
        return self.symbol_table.current_scope

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
        return result

    def match_id(self) -> Optional[ast_.IdAST]:
        token = self.match(TokenID.ID)
        if not token:
            return None

        return ast_.IdAST(token[0])

    def match_type(self) -> Optional[ast_.TypeAST]:
        token = self.match(TokenID.ID)
        if not token:
            return None

        token = token[0]
        type_ = self.symbol_table.resolve_symbol(token.value)
        if type_ is None:
            self.error(token.line, "unknown type {}".format(token.value))

        if not isinstance(type_, ast_.TypeAST):
            self.error(token.line, "{} is not a type".format(token.value))

        return type_

    def match_string_literal(self) -> Optional[ast_.StringLiteralAST]:
        token = self.match(TokenID.STR_LITERAL)
        if not token:
            return

        result = ast_.StringLiteralAST(token[0])
        result.type = self.symbol_table.resolve_symbol('str')
        return result

    def match_char_literal(self) -> Optional[ast_.CharLiteralAST]:
        token = self.match(TokenID.CHAR_LITERAL)
        if not token:
            return

        result = ast_.CharLiteralAST(token[0])
        result.type = self.symbol_table.resolve_symbol('char')
        return result

    def match_primary(self) -> Union[None, ast_.NumericLiteralAST, ast_.StringLiteralAST, ast_.CharLiteralAST]:
        """ Matches a primary expression value
        """
        if self.lookahead in (TokenID.INT_LITERAL, TokenID.FLOAT_LITERAL):
            return self.match_number_literal()
        if self.lookahead == TokenID.STR_LITERAL:
            return self.match_string_literal()
        if self.lookahead == TokenID.CHAR_LITERAL:
            return self.match_char_literal()
        if self.lookahead == TokenID.LP:
            self.match(TokenID.LP)
            result = self.match_binary_or_unary()
            self.match(TokenID.RP)
            return result
        if self.lookahead == TokenID.ID:
            return self.match_id_or_fcall()

        self.error_unexpected_token()
        return None

    def match_unary(self) -> Union[None,
                                   ast_.NumericLiteralAST,
                                   ast_.StringLiteralAST,
                                   ast_.CharLiteralAST,
                                   ast_.UnaryExprAST]:
        if self.lookahead in (TokenID.PLUS, TokenID.MINUS):
            oper = self.lookahead
            self.lookahead = self.lex.get_token()
            if self.lookahead in (TokenID.CHAR_LITERAL, TokenID.STR_LITERAL):
                self.error_unexpected_token()
                return None

            primary = self.match_unary()
            if primary is None:
                return None

            return ast_.UnaryExprAST(op=oper, primary=primary)

        return self.match_primary()

    def match_binary_right_side(self, left: Union[ast_.UnaryExprAST, ast_.BinaryExprAST]) \
            -> Union[None, ast_.UnaryExprAST, ast_.BinaryExprAST]:
        oper = self.lookahead
        self.lookahead = self.lex.get_token()

        right = self.match_unary()
        if right is None:
            return None

        if self.lookahead.value not in OPERATOR_PRECEDENCE or \
                OPERATOR_PRECEDENCE[oper.value] >= OPERATOR_PRECEDENCE[self.lookahead.value]:
            return ast_.BinaryExprAST(op=oper, left=left, right=right)

        # Another operator
        right = self.match_binary_right_side(right)
        if right is None:
            return None

        return ast_.BinaryExprAST(op=oper, left=left, right=right)

    def match_binary_or_unary(self) -> Union[None, ast_.UnaryExprAST, ast_.BinaryExprAST]:
        left = self.match_unary()
        if left is None:
            return None

        while self.lookahead.value in OPERATOR_PRECEDENCE:
            left = self.match_binary_right_side(left)

        return left

    def match_arg_list(self) -> Optional[ast_.ArgListAST]:
        self.match(TokenID.LP)
        args = []

        while True:
            if self.lookahead == TokenID.RP:
                break
            args.append(self.match_binary_or_unary())

            if self.lookahead != TokenID.COMMA:
                break
            self.match(TokenID.COMMA)

        self.match(TokenID.RP)
        return ast_.ArgListAST(args)

    def match_id_or_fcall(self) -> Union[None, ast_.IdAST, ast_.FunctionCallAST]:
        var = self.match_id()
        if self.lookahead != TokenID.LP or var is None:
            return var

        args = self.match_arg_list()
        if args is None:
            return None

        return ast_.FunctionCallAST(name=var, args=args)

    def match_var_assignment(self) -> Optional[ast_.AssignmentAST]:
        var = self.match_id()
        if not var:
            return None

        if not self.match(TokenID.ASSIGN):
            return None

        expr = self.match_binary_or_unary()
        if expr is None:
            return None

        result = ast_.AssignmentAST(var, expr)
        if not self.match(TokenID.SC):
            return None

        return result

    def match_typedecl(self) -> Optional[ast_.TypeAST]:
        token = self.match(TokenID.CO)
        if token is None:
            return None

        return self.match_type()

    def match_var_decl(self) -> Optional[ast_.VarDeclAST]:
        if not self.match(TokenID.VAR):
            return None

        result = self.match_param()  # a param is like a local variable
        if not self.match(TokenID.SC):
            return None

        return result

    def match_return_sentence(self) -> Optional[ast_.ReturnSentenceAST]:
        if not self.match(TokenID.RETURN):
            return None

        expr = None
        if self.lookahead != TokenID.SC:
            expr = self.match_binary_or_unary()
            if expr is None:
                return None

        if not self.match(TokenID.SC):
            return None

        return ast_.ReturnSentenceAST(expr)

    def match_sentence(self) -> Optional[ast_.SentenceAST]:
        if self.lookahead == TokenID.VAR:
            result = self.match_var_decl()
        elif self.lookahead == TokenID.ID and self.peek(1) == TokenID.ASSIGN:
            result = self.match_var_assignment()
        elif self.lookahead == TokenID.IF:
            result = self.match_if_sentence()
        elif self.lookahead == TokenID.WHILE:
            result = self.match_while_sentence()
        elif self.lookahead == TokenID.RETURN:
            result = self.match_return_sentence()
        elif self.lookahead == TokenID.FN:
            result = self.match_funcdecl()
        else:
            result = self.match_binary_or_unary()
            if result is not None:
                tok = self.match(TokenID.SC)
                if not tok:
                    return None

        return result

    def match_if_sentence(self) -> Optional[ast_.IfSentenceAST]:
        if not self.match(TokenID.IF):
            return None
        
        cond = self.match_binary_or_unary()
        if cond is None:
            return None

        then = self.match_sentence_or_block()
        if then is None:
            return None

        if self.lookahead != TokenID.ELSE:
            return ast_.IfSentenceAST(cond, then)

        if not self.match(TokenID.ELSE):
            return None

        else_ = self.match_sentence_or_block()
        if else_ is None:
            return None

        return ast_.IfSentenceAST(cond, then, else_)

    def match_block(self, enter_new_scope: bool = True) -> Optional[ast_.BlockAST]:
        """ Will start a new block (which allows nested variable declarations if a new scope is entered).
        If enter_new_scope is False, the scope remains the same.
        """
        tokens = self.match(TokenID.LBR)
        if not tokens:
            return None

        if enter_new_scope:
            self.start_scope()

        sentences: List[ast_.SentenceAST] = []
        while self.lookahead != TokenID.RBR:
            sentence = self.match_sentence_or_block()
            if sentence is None:
                return None  # syntax error

            sentences.append(sentence)

        tokens = self.match(TokenID.RBR)
        if not tokens:
            return None

        if enter_new_scope:
            self.end_scope()

        return ast_.BlockAST(sentences)

    def match_sentence_or_block(self) -> Union[None, ast_.BlockAST, ast_.SentenceAST]:
        if self.lookahead == TokenID.LBR:
            return self.match_block()

        return self.match_sentence()

    def match_param(self) -> Optional[ast_.VarDeclAST]:
        """ An argument will be treated as a local variable in a new scope
        """
        id_ = self.match_id()
        if not id_:
            return None

        type_ = self.match_typedecl()
        if type_ is None:
            return None

        if not self.symbol_table.declare_symbol(id_.token, type_):
            return None

        return ast_.VarDeclAST(id_, type_)

    def match_param_list(self) -> Optional[ast_.ParamListAST]:
        parameters: List[ast_.VarDeclAST] = []

        if not self.match(TokenID.LP):
            return None

        if self.lookahead != TokenID.RP:
            while True:
                param = self.match_param()
                if param is None:
                    return None
                parameters.append(param)
                if self.lookahead != TokenID.COMMA:
                    break
                self.match(TokenID.COMMA)

        if not self.match(TokenID.RP):
            return None

        return ast_.ParamListAST(parameters)

    def match_funcdecl(self) -> Optional[ast_.FunctionDeclAST]:
        token = self.match(TokenID.FN)
        if not token:
            return None

        func = self.match_id()
        if func is None:
            return None

        self.start_scope(func.var_name)
        params = self.match_param_list()
        if params is None:
            return None

        type_ = self.match_typedecl()
        if type_ is None:
            return None

        block = self.match_block(enter_new_scope=False)
        if block is None:
            return None

        self.end_scope()
        return ast_.FunctionDeclAST(func, paramlist=params, type_=type_, body=block)

    def match_while_sentence(self) -> Optional[ast_.WhileSentenceAST]:
        if not self.match(TokenID.WHILE):
            return None

        cond = self.match_binary_or_unary()
        if cond is None:
            return None

        block = self.match_sentence_or_block()
        if block is None:
            return None

        return ast_.WhileSentenceAST(condition=cond, block=block)

    def parse_program(self) -> Optional[ast_.BlockAST]:
        sentences: List[ast_.SentenceAST] = []
        self.start_scope()  # Main scope
        while self.lookahead != TokenID.EOF:
            sentence = self.match_sentence_or_block()
            if sentence is None:
                return None
            sentences.append(sentence)

        self.end_scope()
        return ast_.BlockAST(sentences=sentences)
