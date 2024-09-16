from __future__ import annotations
from polyeval.misc.utils import ParseError


class Type:
    def __init__(self):
        self.parent: Type = None

    def __str__(self):
        raise NotImplementedError("This method must be implemented by a subclass")

    def type_compatible(self, other_type: Type):
        raise NotImplementedError("This method must be implemented by a subclass")


class VType(Type):
    def __init__(self, value_type: Type):
        super().__init__()
        self.value_type: Type = value_type
        value_type.parent = self


class KVType(VType):
    def __init__(self, key_type: Type, value_type: Type):
        super().__init__(value_type)
        self.key_type: Type = key_type
        key_type.parent = self


class UndeterminedType(Type):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "undetermined"

    def type_compatible(self, other_type: Type):
        return isinstance(other_type, UndeterminedType)

class VoidType(Type):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "void"

    def type_compatible(self, other_type: Type):
        return isinstance(other_type, (VoidType, UndeterminedType))


class BoolType(Type):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "bool"

    def type_compatible(self, other_type: Type):
        return isinstance(other_type, (BoolType, UndeterminedType))


class IntType(Type):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "int"

    def type_compatible(self, other_type: Type):
        return isinstance(other_type, (IntType, UndeterminedType))


class LongType(Type):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "long"

    def type_compatible(self, other_type: Type):
        return isinstance(other_type, (LongType, UndeterminedType))


class DoubleType(Type):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "double"

    def type_compatible(self, other_type: Type):
        return isinstance(other_type, (DoubleType, UndeterminedType))


class CharType(Type):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "char"

    def type_compatible(self, other_type: Type):
        return isinstance(other_type, (CharType, UndeterminedType))


class StringType(Type):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "string"

    def type_compatible(self, other_type: Type):
        return isinstance(other_type, (StringType, UndeterminedType))


class AnyType(Type):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "any"

    def type_compatible(self, other_type: Type):
        return isinstance(
            other_type,
            (
                UndeterminedType,
                BoolType,
                IntType,
                LongType,
                DoubleType,
                CharType,
                StringType,
                AnyType,
            ),
        )


class ListType(VType):
    def __init__(self, value_type: Type):
        super().__init__(value_type)
        if not isinstance(
            value_type,
            (
                UndeterminedType,
                VoidType,
                BoolType,
                IntType,
                LongType,
                DoubleType,
                CharType,
                OptionalType,
                StringType,
                AnyType,
                ListType,
                UnorderedListType,
                DictType,
            ),
        ) or (
            isinstance(value_type, OptionalType)
            and isinstance(value_type.value_type, (MListType, MDictType))
        ):
            raise ParseError(f"`{value_type}` is not a valid value type for `list`")

    def __str__(self):
        return f"list<{self.value_type}>"

    def type_compatible(self, other_type: Type):
        return (isinstance(other_type, ListType) and self.value_type.type_compatible(
            other_type.value_type
        )) or isinstance(other_type, UndeterminedType)


class MListType(VType):
    def __init__(self, value_type: Type):
        super().__init__(value_type)
        if not isinstance(
            value_type,
            (
                UndeterminedType,
                VoidType,
                BoolType,
                IntType,
                LongType,
                DoubleType,
                CharType,
                OptionalType,
                StringType,
                AnyType,
                MListType,
                MDictType,
            ),
        ) or (
            isinstance(value_type, OptionalType)
            and isinstance(
                value_type.value_type, (ListType, DictType, UnorderedListType)
            )
        ):
            print(isinstance(value_type, UndeterminedType))
            raise ParseError(f"`{value_type}` is not a valid value type for `mlist`")

    def __str__(self):
        return f"mlist<{self.value_type}>"

    def type_compatible(self, other_type: Type):
        return (isinstance(other_type, MListType) and self.value_type.type_compatible(
            other_type.value_type
        )) or isinstance(other_type, UndeterminedType)


class UnorderedListType(VType):
    def __init__(self, value_type: Type):
        super().__init__(value_type)
        if not isinstance(
            value_type,
            (
                UndeterminedType,
                VoidType,
                BoolType,
                IntType,
                LongType,
                DoubleType,
                CharType,
                OptionalType,
                StringType,
                AnyType,
                ListType,
                UnorderedListType,
                DictType,
            ),
        ) or (
            isinstance(value_type, OptionalType)
            and isinstance(value_type.value_type, (MListType, MDictType))
        ):
            raise ParseError(
                f"`{value_type}` is not a valid value type for `unorderedlist`"
            )

    def __str__(self):
        return f"unorderedlist<{self.value_type}>"

    def type_compatible(self, other_type: Type):
        return (isinstance(
            other_type, UnorderedListType
        ) and self.value_type.type_compatible(other_type.value_type)) or isinstance(other_type, UndeterminedType)


class DictType(KVType):
    def __init__(self, key_type: Type, value_type: Type):
        super().__init__(key_type, value_type)
        if not isinstance(
            key_type, (UndeterminedType, BoolType, IntType, LongType, CharType, StringType)
        ):
            raise ParseError(f"`{key_type}` is not a valid key type for `dict`")
        if not isinstance(
            value_type,
            (
                UndeterminedType,
                VoidType,
                BoolType,
                IntType,
                LongType,
                DoubleType,
                CharType,
                OptionalType,
                StringType,
                AnyType,
                ListType,
                UnorderedListType,
                DictType,
            ),
        ) or (
            isinstance(value_type, OptionalType)
            and isinstance(value_type.value_type, (MListType, MDictType))
        ):
            raise ParseError(f"`{value_type}` is not a valid value type for `dict`")

    def __str__(self):
        return f"dict<{self.key_type},{self.value_type}>"

    def type_compatible(self, other_type: Type):
        return (
            isinstance(other_type, DictType)
            and self.key_type.type_compatible(other_type.key_type)
            and self.value_type.type_compatible(other_type.value_type)
        ) or isinstance(other_type, UndeterminedType)


class MDictType(KVType):
    def __init__(self, key_type: Type, value_type: Type):
        super().__init__(key_type, value_type)
        if not isinstance(
            key_type, (UndeterminedType, BoolType, IntType, LongType, CharType, StringType)
        ):
            raise ParseError(f"`{key_type}` is not a valid key type for `mdict`")
        if not isinstance(
            value_type,
            (
                UndeterminedType,
                VoidType,
                BoolType,
                IntType,
                LongType,
                DoubleType,
                CharType,
                OptionalType,
                StringType,
                AnyType,
                MListType,
                MDictType,
            ),
        ) or (
            isinstance(value_type, OptionalType)
            and isinstance(
                value_type.value_type, (ListType, DictType, UnorderedListType)
            )
        ):
            raise ParseError(f"`{value_type}` is not a valid value type for `mdict`")

    def __str__(self):
        return f"mdict<{self.key_type},{self.value_type}>"

    def type_compatible(self, other_type: Type):
        return (
            isinstance(other_type, MDictType)
            and self.key_type.type_compatible(other_type.key_type)
            and self.value_type.type_compatible(other_type.value_type)
        ) or isinstance(other_type, UndeterminedType)


class OptionalType(VType):
    def __init__(self, value_type: Type):
        super().__init__(value_type)
        if not isinstance(
            value_type,
            (
                UndeterminedType,
                BoolType,
                IntType,
                LongType,
                DoubleType,
                CharType,
                StringType,
                AnyType,
                ListType,
                MListType,
                UnorderedListType,
                DictType,
                MDictType,
            ),
        ):
            raise ParseError(f"`{value_type}` is not a valid value type for `optional`")

    def __str__(self):
        return f"optional<{self.value_type}>"

    def type_compatible(self, other_type: Type):
        return (
            isinstance(other_type, OptionalType)
            and self.value_type.type_compatible(other_type.value_type)
            or isinstance(other_type, VoidType)
            or self.value_type.type_compatible(other_type)
        ) or isinstance(other_type, UndeterminedType)


class CustomType(Type):
    def __init__(self, name: str):
        super().__init__()
        self.name: str = name

    def __str__(self):
        return self.name

    def type_compatible(self, other_type: Type):
        return (isinstance(other_type, CustomType) and self.name == other_type.name) or isinstance(other_type, UndeterminedType)
