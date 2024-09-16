from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.type import *


class TypeGeneratorRuby(TypeGeneratorBase):
    def __init__(self):
        super().__init__()

    def gen_void(self, t: VoidType):
        return "nil"

    def gen_int(self, t: IntType):
        return "Integer"

    def gen_long(self, t: LongType):
        return "Integer"

    def gen_double(self, t: DoubleType):
        return "Float"

    def gen_char(self, t: CharType):
        return "String"

    def gen_bool(self, t: BoolType):
        return "Boolean"

    def gen_string(self, t: StringType):
        return "String"

    def gen_list(self, t: ListType):
        return f"Array<{self.gen(t.value_type)}>"

    def gen_mlist(self, t: MListType):
        return f"Array<{self.gen(t.value_type)}>"

    def gen_unorderedlist(self, t: UnorderedListType):
        return f"Array<{self.gen(t.value_type)}>"

    def gen_dict(self, t: DictType):
        return f"Hash{{{self.gen(t.key_type)} => {self.gen(t.value_type)}}}"

    def gen_mdict(self, t: MDictType):
        return f"Hash{{{self.gen(t.key_type)} => {self.gen(t.value_type)}}}"

    def gen_optional(self, t: OptionalType):
        return f"{self.gen(t.value_type)}, nil"

    def gen_any(self, t: AnyType):
        return "Object"
