# -*- coding: utf-8 -*-


from lexer import Token, TOKEN_MAP
from abc import ABC, abstractmethod


PRIMITIVE_TYPES = {
    "char": 1,
    "str": None,  # Iterable. sizeof(ptr)
    "int8": 1,
    "uint8": 1,
    "int32": 4,
    "uint32": 4,
    "int64": 8,
    "uint64": 8,
    "float": 8,
}


class AST(ABC):
    @abstractmethod
    def emit(self) -> str:
        pass


class TypeAST(AST, ABC):
    def __init__(self, token: Token):
        self.token = token

    def __repr__(self):
        return 'Type<{}>'.format(self.name)

    @property
    def name(self) -> str:
        return self.token.value


class ScalarTypeAST(TypeAST, ABC):
    """ Scalar types holds a single value
    """


class CompoundTypeAST(TypeAST, ABC):
    """ Compound types holds several elements
    (i.e. arrays, tuples, structs)
    """


class PrimitiveScalarTypeAST(ScalarTypeAST, ABC):
    """ Base class for all primitive types that come defined with the compiler
    """
    def __init__(self, token: Token):
        assert token.value in PRIMITIVE_TYPES, "Invalid type name '{}'".format(token.value)
        assert token.value in TOKEN_MAP and TOKEN_MAP[token.value] == token.id_, \
            "{} does not match type name '{}'".format(str(token.id_), token.value)
        super().__init__(token)


class NumericalTypeAST(PrimitiveScalarTypeAST, ABC):
    """ Any integer of float
    """
    _emmit_C: str = None

    def emit(self) -> str:
        return self._emmit_C


class IntTypeAST(NumericalTypeAST, ABC):
    """ Base class for all primitive integer types
    """
    _min_val: int
    _max_val: int
    _size: int  # Size in bytes

    def __init__(self, token: Token):
        super().__init__(token)
        self._size = PRIMITIVE_TYPES[self.name]

        if self.is_signed:
            self._max_val = (1 << ((self.size << 3) - 1)) - 1
            self._min_val = -(self._max_val + 1)
        else:
            self._max_val = (1 << (8 * self.size)) - 1
            self._min_val = 0

        self._emmit_C = '{}int{}_t'.format(('u', '')[self.is_signed], self.size * 8)

    @property
    def size(self) -> int:
        """ Returns size in bytes
        """
        return self._size

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


class NumericLiteralAST(AST):
    """ A numeric, char o string literal
    """
    def __init__(self, token: Token):
        self.token = token

    def emit(self):
        return self.token.value

