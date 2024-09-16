from __future__ import annotations
import json
import math

from polyeval.misc.utils import ParseError, DebugError

import polyeval.objects.typed_value as ov


class Value:
    def __init__(self, val):
        self.get = val

    def __str__(self):
        raise NotImplementedError("This method must be implemented by a subclass")


class NullValue(Value):
    def __init__(self):
        super().__init__(None)

    def __str__(self):
        return "null"


class BoolValue(Value):
    def __init__(self, val):
        super().__init__(val)
        if not isinstance(val, bool):
            raise DebugError("BoolValue must be initialized with a bool")

    def __str__(self):
        return str(self.get).lower()


class IntValue(Value):
    def __init__(self, val):
        super().__init__(val)
        if not isinstance(val, int):
            raise DebugError("IntValue must be initialized with an int or float")
        if not -2147483648 <= val <= 2147483647:
            raise ParseError(
                "Int value must be within range [-2147483648, 2147483647]."
                "If you want to store large integer, use long instead."
            )

    def __str__(self):
        return str(self.get)


class LongValue(Value):
    def __init__(self, val):
        super().__init__(val)
        if not isinstance(val, int):
            raise DebugError("LongValue must be initialized with an int or float")

    def __str__(self):
        return str(self.get) + "L"


class DoubleValue(Value):
    def __init__(self, val):
        super().__init__(val)
        if not isinstance(val, (float, int)):
            raise DebugError("DoubleValue must be initialized with an int or float")

    def __str__(self):
        if math.isnan(self.get):
            return "nan"
        elif math.isinf(self.get):
            if self.get > 0:
                return "inf"
            else:
                return "-inf"
        if isinstance(self.get, int) or self.get.is_integer():
            return str(int(self.get)) + ".0"
        return "{:.6f}".format(self.get).rstrip("0")


class CharValue(Value):
    def __init__(self, val):
        if not isinstance(val, str):
            raise DebugError("CharValue must be initialized with a str")
        try:
            new_val = '"' + val[1:-1] + '"'
            new_str_value = json.loads(new_val)
            if len(new_str_value) != 1:
                raise ParseError("Char value must have a string of length 1")
            super().__init__(new_str_value)
        except json.JSONDecodeError:
            raise ParseError("Char value must follow json escape rules")

    def __str__(self):
        return "'" + json.dumps(self.get)[1:-1] + "'"


class StringValue(Value):
    def __init__(self, val):
        if not isinstance(val, str):
            raise DebugError("StringValue must be initialized with a str")
        try:
            new_str_value = json.loads(val)
            super().__init__(new_str_value)
        except json.JSONDecodeError:
            raise ParseError("String value must follow json string rules")

    def __str__(self):
        return json.dumps(self.get)


class ListValue(Value):
    def __init__(self, val):
        if not isinstance(val, list):
            raise DebugError("ListValue must be initialized with a list")
        for item in val:
            if not isinstance(item, ov.TypedValue):
                raise DebugError(
                    f"ListValue item must be type of `TypedValue`, but found {type(item)}"
                )
        super().__init__(val)

    def __str__(self):
        return "[" + ", ".join([str(item) for item in self.get]) + "]"


class DictValue(Value):
    def __init__(self, val):
        if not isinstance(val, list):
            raise DebugError("DictValue must be initialized with a list")
        if len(val) % 2 != 0:
            raise DebugError("DictValue must be initialized with a list of even length")
        dict_val = {}
        for idx, item in enumerate(val):
            if idx % 2 == 0:
                if not isinstance(item, ov.TypedValue):
                    raise DebugError(
                        f"DictValue key must be type of `TypedValue`, but found `{type(item)}`"
                    )
                if item in dict_val:
                    raise ParseError(f"Duplicate dict key `{item}` found")
                dict_val[item] = val[idx + 1]
            else:
                if not isinstance(item, ov.TypedValue):
                    raise DebugError(
                        f"DictValue value must be type of `TypedValue`, but found `{type(item)}`"
                    )
        super().__init__(dict_val)

    def __str__(self):
        return (
            "{"
            + ", ".join([str(key) + " => " + str(self.get[key]) for key in self.get])
            + "}"
        )
