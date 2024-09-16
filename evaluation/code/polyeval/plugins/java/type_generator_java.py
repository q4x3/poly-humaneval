from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.type import *


class TypeGeneratorJava(TypeGeneratorBase):
    def __init__(self):
        super().__init__()

    def gen_void(self, t: VoidType):
        if t.parent is not None:
            return "Void"
        return "void"

    def gen_int(self, t: IntType):
        if t.parent is not None:
            return "Integer"
        return "int"

    def gen_long(self, t: LongType):
        if t.parent is not None:
            return "Long"
        return "long"

    def gen_double(self, t: DoubleType):
        if t.parent is not None:
            return "Double"
        return "double"

    def gen_char(self, t: CharType):
        if t.parent is not None:
            return "Character"
        return "char"

    def gen_bool(self, t: BoolType):
        if t.parent is not None:
            return "Boolean"
        return "boolean"

    def gen_string(self, t: StringType):
        return "String"

    def gen_list(self, t: ListType):
        return f"List<{self.gen(t.value_type)}>"

    def gen_mlist(self, t: MListType):
        return f"ArrayList<{self.gen(t.value_type)}>"

    def gen_unorderedlist(self, t: UnorderedListType):
        return f"List<{self.gen(t.value_type)}>"

    def gen_dict(self, t: DictType):
        return f"Map<{self.gen(t.key_type)}, {self.gen(t.value_type)}>"

    def gen_mdict(self, t: MDictType):
        return f"HashMap<{self.gen(t.key_type)}, {self.gen(t.value_type)}>"

    def gen_optional(self, t: OptionalType):
        return f"Optional<{self.gen(t.value_type)}>"

    def gen_any(self, t: AnyType):
        return "Object"
