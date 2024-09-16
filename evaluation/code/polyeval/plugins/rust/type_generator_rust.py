from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.type import *


class TypeGeneratorRust(TypeGeneratorBase):
    def __init__(self):
        super().__init__()

    def gen_void(self, t: VoidType):
        return "()"

    def gen_int(self, t: IntType):
        return "i32"

    def gen_long(self, t: LongType):
        return "i64"

    def gen_double(self, t: DoubleType):
        return "f64"

    def gen_char(self, t: CharType):
        return "char"

    def gen_bool(self, t: BoolType):
        return "bool"

    def gen_string(self, t: StringType):
        return "String"

    def gen_list(self, t: ListType):
        return f"Vec<{self.gen(t.value_type)}>"

    def gen_mlist(self, t: MListType):
        return f"Vec<{self.gen(t.value_type)}>"

    def gen_unorderedlist(self, t: UnorderedListType):
        return f"Vec<{self.gen(t.value_type)}>"

    def gen_dict(self, t: DictType):
        return f"HashMap<{self.gen(t.key_type)},{self.gen(t.value_type)}>"

    def gen_mdict(self, t: MDictType):
        return f"HashMap<{self.gen(t.key_type)},{self.gen(t.value_type)}>"

    def gen_optional(self, t: OptionalType):
        return f"Option<{self.gen(t.value_type)}>"

    def gen_any(self, t: AnyType):
        return "Box<dyn Any>"
