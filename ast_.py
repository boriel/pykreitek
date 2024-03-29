# -*- coding: utf-8 -*-


from lexer import Token
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import List, Union, Optional


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
    def __init__(self, token: Token, emit_str: str = None):
        assert token.value in PRIMITIVE_TYPES, "Invalid type name '{}'".format(token.value)
        super().__init__(token)
        if emit_str is None:
            emit_str = self.name
        self._size = PRIMITIVE_TYPES[self.name]
        self._emit_C = emit_str

    def emit(self) -> str:
        return self._emit_C

    @property
    def size(self) -> int:
        """ Returns size in bytes
        """
        return self._size


class NumericalTypeAST(PrimitiveScalarTypeAST):
    """ Any integer of float
    """
    _emit_C: str = None


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


class SentenceAST(AST, ABC):
    pass


class ExpressionAST(AST, ABC):
    pass


class UnaryExprAST(ExpressionAST):
    type_: TypeAST

    def __init__(self, op: Token, primary: Union[CharLiteralAST, StringLiteralAST, IdAST]):
        self.primary = primary
        self.op = op

    def emit(self) -> str:
        return "{}{}".format(self.op.value, self.primary.emit())


class BinaryExprAST(ExpressionAST):
    type_: TypeAST

    def __init__(self, op: Token, left: UnaryExprAST, right: UnaryExprAST):
        self.op = op
        self.left = left
        self.right = right

    def emit(self) -> str:
        return "({} {} {})".format(self.left.emit(), self.op.value, self.right.emit())


class ArgListAST(AST):
    def __init__(self, arg_list: List[AST]):
        self.args = arg_list

    def emit(self) -> str:
        return '({})'.format(', '.join(x.emit() for x in self.args))


class FunctionCallAST(ExpressionAST):
    type_: TypeAST

    def __init__(self, name: IdAST, args: ArgListAST):
        self.name = name
        self.args = args

    def emit(self) -> str:
        return '{}({})'.format(self.name.var_name, ', '.join(arg.emit() for arg in self.args.args))


class AssignmentAST(SentenceAST):
    def __init__(self, lvalue: IdAST, rvalue: Union[BinaryExprAST, UnaryExprAST]):
        self.lvalue = lvalue
        self.rvalue = rvalue

    def emit(self) -> str:
        return '{} = {}'.format(self.lvalue.emit(), self.rvalue.emit())


class VarDeclAST(SentenceAST):
    def __init__(self, var: IdAST, type_: TypeAST):
        self.var = var
        self.type_ = type_

    def emit(self) -> str:
        return '{} {}'.format(self.type_.name, self.var.var_name)


class BlockAST(SentenceAST):
    def __init__(self, sentences: List[SentenceAST]):
        self.sentences = sentences

    def emit(self) -> str:
        return '{{\n{}}}'.format(''.join('{};\n'.format(x.emit()) for x in self.sentences))


class ParamListAST(AST):
    def __init__(self, parameters: List[VarDeclAST]):
        self.parameters = parameters

    def emit(self) -> str:
        return '({})'.format(', '.join(x.emit() for x in self.parameters))


class FunctionDeclAST(AST):
    def __init__(self, func: IdAST, paramlist: ParamListAST, type_: TypeAST, body: BlockAST):
        self.func = func
        self.parameters = paramlist
        self.type_ = type_
        self.body = body

    @property
    def name(self) -> str:
        return self.func.var_name

    def emit(self) -> str:
        return '{} {}{} {}'.format(self.type_.emit(), self.name, self.parameters.emit(), self.body.emit())


class IfSentenceAST(SentenceAST):
    def __init__(self, condition: ExpressionAST, then: BlockAST, else_: BlockAST = None):
        self.condition = condition
        self.then = then
        self.else_ = else_

    def emit(self) -> str:
        if self.else_ is None:
            return "if ({}) {{\n{}\n}}".format(self.condition.emit(), self.then.emit())
        return "if ({}) {{\n{}\n}} else {{\n{}\n}}".format(self.condition.emit(), self.then.emit(), self.else_.emit())


class WhileSentenceAST(SentenceAST):
    def __init__(self, condition: ExpressionAST, block: BlockAST):
        self.condition = condition
        self.block = block

    def emit(self) -> str:
        return 'while ({}) {{\n{}\n}}'.format(self.condition.emit(), self.block.emit())


class ReturnSentenceAST(SentenceAST):
    def __init__(self, value: Optional[ExpressionAST]):
        self.value = value

    def emit(self) -> str:
        return 'return{};'.format(' {}'.format(self.value.emit()) if self.value is not None else '')
