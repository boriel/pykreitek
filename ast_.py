# -*- coding: utf-8 -*-


from lexer import Token, TOKEN_MAP
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Optional, Union


PRIMITIVE_TYPES = OrderedDict([
    ("int8", 1),
    ("uint8", 1),
    ("int32", 4),
    ("uint32", 4),
    ("int64", 8),
    ("uint64", 8),
    ("float", 8),
    ("bool", 1),
    ("char", 1),
    ("str", 8),  # Iterable. sizeof(ptr) => 8 for x64, 4 for x86
])


class AST(ABC):
    @abstractmethod
    def emit(self) -> str:
        pass


class TokenAST(AST, ABC):
    """ Abstract base class for basic AST symbols which are mostly terminals
    """
    def __init__(self, token: Token):
        self.token = token


class TypeAST(TokenAST, ABC):
    def __repr__(self):
        return 'Type<{}>'.format(self.name)

    @property
    def name(self) -> str:
        return self.token.value


class ScalarLiteralAST(TokenAST, ABC):
    @property
    def value(self) -> str:
        return self.token.value


class ScalarTypeAST(TypeAST, ABC):
    """ Scalar types holds a single value
    """


class CompoundTypeAST(TypeAST, ABC):
    """ Compound types holds several elements
    (i.e. arrays, tuples, structs)
    """


class PrimitiveScalarTypeAST(ScalarTypeAST):
    """ Base class for all primitive types that come defined with the compiler
    """
    def __init__(self, token: Token, emmit_str: str = ''):
        assert token.value in PRIMITIVE_TYPES, "Invalid type name '{}'".format(token.value)
        assert token.value in TOKEN_MAP and TOKEN_MAP[token.value] == token.id_, \
            "{} does not match type name '{}'".format(str(token.id_), token.value)
        super().__init__(token)
        self._size = PRIMITIVE_TYPES[self.name]
        self._emmit_C = emmit_str

    def emit(self) -> str:
        return self._emmit_C

    @property
    def size(self) -> int:
        """ Returns size in bytes
        """
        return self._size


class NumericalTypeAST(PrimitiveScalarTypeAST):
    """ Any integer of float
    """
    _emmit_C: str = None


class IntTypeAST(NumericalTypeAST, ABC):
    """ Base class for all primitive integer types
    """
    _min_val: int
    _max_val: int
    _size: int  # Size in bytes

    def __init__(self, token: Token):
        super().__init__(token)

        if self.is_signed:
            self._max_val = (1 << ((self.size << 3) - 1)) - 1
            self._min_val = -(self._max_val + 1)
        else:
            self._max_val = (1 << (8 * self.size)) - 1
            self._min_val = 0

        self._emmit_C = '{}int{}_t'.format(('u', '')[self.is_signed], self.size * 8)

    @property
    def min_val(self) -> int:
        return self._min_val

    @property
    def max_val(self) -> int:
        return self._max_val

    @property
    @abstractmethod
    def is_signed(self) -> bool:
        pass


class SignedIntType(IntTypeAST):
    @property
    def is_signed(self) -> bool:
        return True


class UnsignedIntType(IntTypeAST):
    @property
    def is_signed(self) -> bool:
        return False


class NumericLiteralAST(TokenAST):
    """ A numeric, char o string literal
    """
    def __init__(self, token: Token, type_: ScalarTypeAST):
        super().__init__(token)
        self.type = type_

        if isinstance(type_, (SignedIntType, UnsignedIntType)):
            assert type_.min_val <= token.num_val <= type_.max_val,\
                "Value {} not in range [{}..{}] for type {}".format(
                    token.value, type_.min_val, type_.max_val, type_.name)

    def emit(self):
        return self.token.value

    @property
    def value(self) -> str:
        return self.token.value


class IdAST(TokenAST):
    """ An identifier (can be a variable or function name)
    """
    @property
    def var_name(self) -> str:
        return self.token.value

    def emit(self) -> str:
        return self.var_name


class StringLiteralAST(ScalarLiteralAST):
    type: ScalarTypeAST

    def emit(self) -> str:
        return '"{}"'.format(self.value)


class CharLiteralAST(ScalarLiteralAST):
    type: ScalarTypeAST

    def emit(self) -> str:
        return "'{}'".format(self.value)


class UnaryExprAST(AST):
    type_: TypeAST

    def __init__(self, op: Token, primary: Union[CharLiteralAST, StringLiteralAST, IdAST]):
        self.primary = primary
        self.op = op

    def emit(self) -> str:
        return "{}{}".format(self.op.value, self.primary.emit())
