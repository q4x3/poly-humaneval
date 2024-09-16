from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.type import *


class TypeGeneratorKotlin(TypeGeneratorBase):
    def __init__(self):
        super().__init__()

    def gen_void(self, t: VoidType):
        return "Unit"

    def gen_int(self, t: IntType):
        return "Int"

    def gen_long(self, t: LongType):
        return "Long"

    def gen_double(self, t: DoubleType):
        return "Double"

    def gen_char(self, t: CharType):
        return "Char"

    def gen_bool(self, t: BoolType):
        return "Boolean"

    def gen_string(self, t: StringType):
        return "String"

    def gen_list(self, t: ListType):
        return f"List<{self.gen(t.value_type)}>"

    def gen_mlist(self, t: MListType):
        return f"MutableList<{self.gen(t.value_type)}>"

    def gen_unorderedlist(self, t: UnorderedListType):
        return f"List<{self.gen(t.value_type)}>"

    def gen_dict(self, t: DictType):
        return f"Map<{self.gen(t.key_type)},{self.gen(t.value_type)}>"

    def gen_mdict(self, t: MDictType):
        return f"MutableMap<{self.gen(t.key_type)},{self.gen(t.value_type)}>"

    def gen_optional(self, t: OptionalType):
        return f"{self.gen(t.value_type)}?"

    def gen_any(self, t: AnyType):
        return "Any"
