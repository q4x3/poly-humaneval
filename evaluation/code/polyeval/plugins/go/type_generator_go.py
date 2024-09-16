from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.type import *


class TypeGeneratorGo(TypeGeneratorBase):
    def __init__(self):
        super().__init__()

    def gen_void(self, t: VoidType):
        return ""

    def gen_int(self, t: IntType):
        return "int"

    def gen_long(self, t: LongType):
        return "int64"

    def gen_double(self, t: DoubleType):
        return "float64"

    def gen_char(self, t: CharType):
        return "rune"

    def gen_bool(self, t: BoolType):
        return "bool"

    def gen_string(self, t: StringType):
        return "string"

    def gen_list(self, t: ListType):
        return f"[]{self.gen(t.value_type)}"

    def gen_mlist(self, t: MListType):
        return f"[]{self.gen(t.value_type)}"

    def gen_unorderedlist(self, t: UnorderedListType):
        return f"[]{self.gen(t.value_type)}"

    def gen_dict(self, t: DictType):
        return f"map[{self.gen(t.key_type)}]{self.gen(t.value_type)}"

    def gen_mdict(self, t: MDictType):
        return f"map[{self.gen(t.key_type)}]{self.gen(t.value_type)}"

    def gen_optional(self, t: OptionalType):
        if not isinstance(t.value_type, VType):
            return f"*{self.gen(t.value_type)}"
        else:
            return self.gen(t.value_type)

    def gen_any(self, t: AnyType):
        return "interface{}"
