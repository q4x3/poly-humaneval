from __future__ import annotations

from polyeval.generators.base import *
from polyeval.plugins.java.type_generator_java import TypeGeneratorJava
from polyeval.objects.value import *
from polyeval.objects.typed_value import *


class ValueGeneratorJava(ValueGeneratorBase):
    def __init__(self):
        super().__init__()
        self.type_generator = TypeGeneratorJava()

    def gen_void(self):
        return "null"

    def gen_int(self, tv: IntTypedValue):
        val = tv.value.get
        return str(val)

    def gen_long(self, tv: LongTypedValue):
        val = tv.value.get
        return str(val) + "L"

    def gen_double(self, tv: DoubleTypedValue):
        val = tv.value.get
        if math.isnan(val):
            return "Double.NaN"
        elif math.isinf(val):
            if val > 0:
                return "Double.POSITIVE_INFINITY"
            else:
                return "Double.NEGATIVE_INFINITY"
        value_str = "{:.6f}".format(val).rstrip("0")
        if value_str.endswith("."):
            value_str += "0"
        if value_str == "-0.0":
            value_str = "0.0"
        return value_str

    def gen_char(self, tv: CharTypedValue):
        val = tv.value.get
        return f"'{json.dumps(val)[1:-1]}'"

    def gen_bool(self, tv: BoolTypedValue):
        val = tv.value.get
        return "true" if val else "false"

    def gen_string(self, tv: StringTypedValue):
        val = tv.value.get
        return json.dumps(val)

    def gen_list(self, tv: ListTypedValue):
        val = tv.value.get
        v_strs = [self.gen(value) for value in val]
        v_str = ", ".join(v_strs)
        type_str = self.type_generator.gen(tv.type.value_type)
        return f"List.of({v_str})"

    def gen_mlist(self, tv: MListTypedValue):
        val = tv.value.get
        v_strs = [self.gen(value) for value in val]
        v_str = ", ".join(v_strs)
        type_str = self.type_generator.gen(tv.type)
        return f"new {type_str}(List.of({v_str}))"

    def gen_unorderedlist(self, tv: UnorderedListTypedValue):
        val = tv.value.get
        v_strs = sorted([self.gen(value) for value in val])
        v_str = ", ".join(v_strs)
        type_str = self.type_generator.gen(tv.type.value_type)
        return f"List.of({v_str})"

    def gen_dict(self, tv: DictTypedValue):
        val = tv.value.get
        keys = [self.gen(key) for key in val.keys()]
        values = [self.gen(value) for value in val.values()]
        kv_strs = sorted(
            [f"Map.entry({key}, {value})" for key, value in zip(keys, values)]
        )
        kv_str = ", ".join(kv_strs)
        type_str = self.type_generator.gen(tv.type.key_type) + ", " + self.type_generator.gen(tv.type.value_type)
        return f"Map.ofEntries({kv_str})"

    def gen_mdict(self, tv: MDictTypedValue):
        val = tv.value.get
        keys = [self.gen(key) for key in val.keys()]
        values = [self.gen(value) for value in val.values()]
        kv_strs = sorted(
            [f"Map.entry({key}, {value})" for key, value in zip(keys, values)]
        )
        kv_str = ", ".join(kv_strs)
        type_str = self.type_generator.gen(tv.type)
        return f"new {type_str}(Map.ofEntries({kv_str}))"

    def gen_optional(self, tv: TypedValue):
        return f"Optional.ofNullable({self.gen_non_optional_value(tv)})"

    def gen_optional_void(self):
        return "Optional.ofNullable(null)"

    def gen_any(self, tv: TypedValue):
        return self.gen_non_optional_any_value(tv)
