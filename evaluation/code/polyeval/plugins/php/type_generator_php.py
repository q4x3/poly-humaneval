from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.type import *


class TypeGeneratorPhp(TypeGeneratorBase):
    def __init__(self):
        super().__init__()

    def gen_void(self, t: VoidType):
        return "void"

    def gen_int(self, t: IntType):
        return "int"

    def gen_long(self, t: LongType):
        return "int"

    def gen_double(self, t: DoubleType):
        return "float"

    def gen_char(self, t: CharType):
        return "string"

    def gen_bool(self, t: BoolType):
        return "bool"

    def gen_string(self, t: StringType):
        return "string"

    def gen_list(self, t: ListType):
        return f"array<{self.gen(t.value_type)}>"

    def gen_mlist(self, t: MListType):
        return f"array<{self.gen(t.value_type)}>"

    def gen_unorderedlist(self, t: UnorderedListType):
        return f"array<{self.gen(t.value_type)}>"

    def gen_dict(self, t: DictType):
        return f"array<{self.gen(t.key_type)}, {self.gen(t.value_type)}>"

    def gen_mdict(self, t: MDictType):
        return f"array<{self.gen(t.key_type)}, {self.gen(t.value_type)}>"

    def gen_optional(self, t: OptionalType):
        if isinstance(t.value_type, AnyType):
            return self.gen(t.value_type)
        return f"{self.gen(t.value_type)} | null"

    def gen_any(self, t: AnyType):
        return "mixed"
