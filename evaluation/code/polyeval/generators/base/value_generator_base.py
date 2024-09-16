from __future__ import annotations

import copy

from polyeval.objects.type import *
from polyeval.objects.value import *
from polyeval.objects.typed_value import *


class ValueGeneratorBase:
    def __init__(self):
        pass

    def gen_void(self):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_int(self, tv: IntTypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_long(self, tv: LongTypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_double(self, tv: DoubleTypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_char(self, tv: CharTypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_bool(self, tv: BoolTypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_string(self, tv: StringTypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_list(self, tv: ListTypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_mlist(self, tv: MListTypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_unorderedlist(self, tv: UnorderedListTypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_dict(self, tv: DictTypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_mdict(self, tv: MDictTypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_optional(self, tv: TypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_optional_void(self):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_any(self, tv: TypedValue):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen(self, tv: TypedValue):
        t = tv.type
        if isinstance(t, OptionalType):
            if isinstance(tv, VoidTypedValue):
                return self.gen_optional_void()
            else:
                new_tv = copy.deepcopy(tv)
                new_tv.type = t.value_type
                return self.gen_optional(new_tv)
        return self.gen_non_optional_value(tv)

    def gen_non_optional_value(self, tv: TypedValue):
        if isinstance(tv.type, AnyType):
            return self.gen_any(tv)
        else:
            return self.gen_non_optional_any_value(tv)

    def gen_non_optional_any_value(self, tv: TypedValue):
        if isinstance(tv, VoidTypedValue):
            return self.gen_void()
        if isinstance(tv, IntTypedValue):
            return self.gen_int(tv)
        if isinstance(tv, LongTypedValue):
            return self.gen_long(tv)
        if isinstance(tv, DoubleTypedValue):
            return self.gen_double(tv)
        if isinstance(tv, CharTypedValue):
            return self.gen_char(tv)
        if isinstance(tv, BoolTypedValue):
            return self.gen_bool(tv)
        if isinstance(tv, StringTypedValue):
            return self.gen_string(tv)
        if isinstance(tv, ListTypedValue):
            return self.gen_list(tv)
        if isinstance(tv, MListTypedValue):
            return self.gen_mlist(tv)
        if isinstance(tv, UnorderedListTypedValue):
            return self.gen_unorderedlist(tv)
        if isinstance(tv, DictTypedValue):
            return self.gen_dict(tv)
        if isinstance(tv, MDictTypedValue):
            return self.gen_mdict(tv)
        raise ValueError(f"Unknown data value: {tv}")
