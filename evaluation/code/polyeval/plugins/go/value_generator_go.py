from __future__ import annotations

from polyeval.generators.base import *
from polyeval.plugins.go.type_generator_go import TypeGeneratorGo
from polyeval.objects.type import *
from polyeval.objects.value import *
from polyeval.objects.typed_value import *


class ValueGeneratorGo(ValueGeneratorBase):
    def __init__(self):
        super().__init__()
        self.type_generator = TypeGeneratorGo()

    def gen_void(self):
        return "nil"

    def gen_int(self, tv: IntTypedValue):
        val = tv.value.get
        return str(val)

    def gen_long(self, tv: LongTypedValue):
        val = tv.value.get
        return f"int64({str(val)})"

    def gen_double(self, tv: DoubleTypedValue):
        val = tv.value.get
        if math.isnan(val):
            return "math.NaN()"
        elif math.isinf(val):
            if val > 0:
                return "math.Inf(1)"
            else:
                return "math.Inf(-1)"
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
        type_str = self.type_generator.gen(tv.type)
        return f"{type_str}{{{v_str}}}"

    def gen_mlist(self, tv: MListTypedValue):
        val = tv.value.get
        v_strs = [self.gen(value) for value in val]
        v_str = ", ".join(v_strs)
        type_str = self.type_generator.gen(tv.type)
        return f"{type_str}{{{v_str}}}"

    def gen_unorderedlist(self, tv: UnorderedListTypedValue):
        val = tv.value.get
        v_strs = sorted([self.gen(value) for value in val])
        v_str = ", ".join(v_strs)
        type_str = self.type_generator.gen(tv.type)
        return f"{type_str}{{{v_str}}}"

    def gen_dict(self, tv: DictTypedValue):
        val = tv.value.get
        keys = [self.gen(key) for key in val.keys()]
        values = [self.gen(value) for value in val.values()]
        kv_strs = sorted([f"{key}:{value}" for key, value in zip(keys, values)])
        kv_str = ", ".join(kv_strs)
        type_str = self.type_generator.gen(tv.type)
        return f"{type_str}{{{kv_str}}}"

    def gen_mdict(self, tv: MDictTypedValue):
        val = tv.value.get
        keys = [self.gen(key) for key in val.keys()]
        values = [self.gen(value) for value in val.values()]
        kv_strs = sorted([f"{key}:{value}" for key, value in zip(keys, values)])
        kv_str = ", ".join(kv_strs)
        type_str = self.type_generator.gen(tv.type)
        return f"{type_str}{{{kv_str}}}"

    def gen_optional(self, tv: TypedValue):
        if isinstance(tv.type, VType):
            return self.gen_non_optional_value(tv)
        else:
            return f"&[]{self.type_generator.gen(tv.type)}{{{self.gen(tv)}}}[0]"

    def gen_optional_void(self):
        return "nil"

    def gen_any(self, tv: TypedValue):
        return self.gen_non_optional_any_value(tv)
