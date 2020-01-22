# -*- coding: utf-8 -*-


from lexer import Token, TOKEN_MAP, PRIMITIVE_TYPES
from abc import ABC, abstractmethod


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
    def __init__(self, type_name: str):
        assert type_name in PRIMITIVE_TYPES, "Invalid type name '{}'".format(type_name)
        token = Token(TOKEN_MAP[type_name], 0, 0, type_name)
        super().__init__(token)


class NumericalTypeAST(PrimitiveScalarTypeAST, ABC):
    """ Any integer of float
    """
    _name = None

    def __init__(self):
        super().__init__(self._name)


class IntTypeAST(NumericalTypeAST, ABC):
    """ Base class for all primitive integer types
    """
    _min_val: int
    _max_val: int
    _size: int  # Size in bytes

    def __init__(self):
        super().__init__()

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
    _name = 'int8'

    def emit(self) -> str:
        return 'int8_t'


class TypeU8AST(UnsignedIntType):
    _size = 1
    _name = 'uint8'

    def emit(self) -> str:
        return 'uint8_t'


class TypeI32AST(SignedIntType):
    _size = 4
    _name = 'int32'

    def emit(self) -> str:
        return 'int32_t'


class TypeU32AST(UnsignedIntType):
    _size = 4
    _name = 'uint32'

    def emit(self) -> str:
        return 'uint32_t'


class TypeI64AST(SignedIntType):
    _size = 8
    _name = 'int64'

    def emit(self) -> str:
        return 'int64_t'


class TypeU64AST(UnsignedIntType):
    _size = 8
    _name = 'uint64'

    def emit(self) -> str:
        return 'uint64_t'


class TypeFloatAST(NumericalTypeAST):
    _size = 8
    _name = 'float'

    def emit(self) -> str:
        return 'double'


class NumericLiteralAST(AST):
    """ A numeric, char o string literal
    """
    def __init__(self, token: Token):
        self.token = token

    def emit(self):
        return self.token.value

