from __future__ import annotations

from polyeval.objects.type import *


class TypeGeneratorBase:
    def __init__(self):
        pass

    def gen_void(self, t: VoidType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_int(self, t: IntType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_long(self, t: LongType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_double(self, t: DoubleType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_char(self, t: CharType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_bool(self, t: BoolType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_string(self, t: StringType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_list(self, t: ListType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_mlist(self, t: MListType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_unorderedlist(self, t: UnorderedListType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_dict(self, t: DictType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_mdict(self, t: MDictType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_optional(self, t: OptionalType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_any(self, t: AnyType):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen(self, t: Type):
        if isinstance(t, VoidType):
            return self.gen_void(t)
        if isinstance(t, IntType):
            return self.gen_int(t)
        if isinstance(t, LongType):
            return self.gen_long(t)
        if isinstance(t, DoubleType):
            return self.gen_double(t)
        if isinstance(t, CharType):
            return self.gen_char(t)
        if isinstance(t, BoolType):
            return self.gen_bool(t)
        if isinstance(t, StringType):
            return self.gen_string(t)
        if isinstance(t, ListType):
            return self.gen_list(t)
        if isinstance(t, MListType):
            return self.gen_mlist(t)
        if isinstance(t, UnorderedListType):
            return self.gen_unorderedlist(t)
        if isinstance(t, DictType):
            return self.gen_dict(t)
        if isinstance(t, MDictType):
            return self.gen_mdict(t)
        if isinstance(t, OptionalType):
            return self.gen_optional(t)
        if isinstance(t, AnyType):
            return self.gen_any(t)
        else:
            raise ValueError(f"Unknown data type: {t}")
