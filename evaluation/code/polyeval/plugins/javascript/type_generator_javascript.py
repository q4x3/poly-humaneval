from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.type import *


class TypeGeneratorJavascript(TypeGeneratorBase):
    def __init__(self):
        super().__init__()

    def gen_void(self, t: VoidType):
        return "null"

    def gen_int(self, t: IntType):
        return "number"

    def gen_long(self, t: LongType):
        return "number"

    def gen_double(self, t: DoubleType):
        return "number"

    def gen_char(self, t: CharType):
        return "string"

    def gen_bool(self, t: BoolType):
        return "boolean"

    def gen_string(self, t: StringType):
        return "string"

    def gen_list(self, t: ListType):
        return f"Array<{self.gen(t.value_type)}>"

    def gen_mlist(self, t: MListType):
        return f"Array<{self.gen(t.value_type)}>"

    def gen_unorderedlist(self, t: UnorderedListType):
        return f"Array<{self.gen(t.value_type)}>"

    def gen_dict(self, t: DictType):
        return f"Map<{self.gen(t.key_type)}, {self.gen(t.value_type)}>"

    def gen_mdict(self, t: MDictType):
        return f"Map<{self.gen(t.key_type)}, {self.gen(t.value_type)}>"

    def gen_optional(self, t: OptionalType):
        if isinstance(t.value_type, AnyType):
            return self.gen(t.value_type)
        return f"?{self.gen(t.value_type)}"

    def gen_any(self, t: AnyType):
        return "*"
