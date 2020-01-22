# -*- coding: utf-8 -*-


from lexer import Token
from abc import ABC, abstractmethod


class AST(ABC):
    @abstractmethod
    def emit(self) -> str:
        pass


class TypeAST(AST, ABC):
    def __init__(self, token: Token):
        self.token = token

    def __repr__(self):
        return 'Type<{}>'.format(self.token.id_)


class ScalarTypeAST(TypeAST, ABC):
    """ Scalar types holds a single value
    """


class CompoundTypeAST(TypeAST, ABC):
    """ Compound types holds several elements
    (i.e. arrays, tuples, structs)
    """


class IntTypeAST(ScalarTypeAST, ABC):
    """ Base class for all integer types
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


class SignedIntType(IntTypeAST, ABC):
    @property
    def is_signed(self) -> bool:
        return True


class UnsignedIntType(IntTypeAST, ABC):
    @property
    def is_signed(self) -> bool:
        return False


class TypeI8AST(SignedIntType):
    _size = 1

    def emit(self) -> str:
        return 'int8_t'


class TypeU8AST(UnsignedIntType):
    _size = 1

    def emit(self) -> str:
        return 'uint8_t'


class NumericLiteralAST(AST):
    """ A numeric, char o string literal
    """
    def __init__(self, token: Token):
        self.token = token

    def emit(self):
        return self.token.value

