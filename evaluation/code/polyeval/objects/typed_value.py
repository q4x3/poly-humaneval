from __future__ import annotations
from typing import Optional

import polyeval.objects.type as ot
import polyeval.objects.value as ov
from polyeval.misc.utils import ParseError, DebugError


def list_type_infer(items: list[ov.TypedValue]) -> Optional[ot.Type]:
    if len(items) == 0:
        return ot.UndeterminedType()

    most_compatible_type = items[0].type
    for item in items:
        if not item.type.type_compatible(
            most_compatible_type
        ) and not most_compatible_type.type_compatible(item.type):
            most_compatible_type = None
            break
        elif item.type.type_compatible(most_compatible_type):
            most_compatible_type = item.type
    if most_compatible_type is not None:
        return most_compatible_type

    not_null_items = [item for item in items if not isinstance(item.type, ot.VoidType)]
    most_compatible_type = not_null_items[0].type
    for item in not_null_items:
        if not item.type.type_compatible(
            most_compatible_type
        ) and not most_compatible_type.type_compatible(item.type):
            most_compatible_type = None
            break
        elif item.type.type_compatible(most_compatible_type):
            most_compatible_type = item.type

    if most_compatible_type is not None:
        return ot.OptionalType(most_compatible_type)

    return None


def get_typed_value_without_type(value: ov.Value) -> TypedValue:
    if isinstance(value, ov.NullValue):
        return VoidTypedValue(value)
    elif isinstance(value, ov.BoolValue):
        return BoolTypedValue(value)
    elif isinstance(value, ov.IntValue):
        return IntTypedValue(value)
    elif isinstance(value, ov.LongValue):
        return LongTypedValue(value)
    elif isinstance(value, ov.DoubleValue):
        return DoubleTypedValue(value)
    elif isinstance(value, ov.CharValue):
        return CharTypedValue(value)
    elif isinstance(value, ov.StringValue):
        return StringTypedValue(value)
    elif isinstance(value, ov.ListValue):
        infered_type = list_type_infer(value.get)
        if infered_type is None:
            raise ParseError(f"Cannot infer type of list {value}")
        else:
            return ListTypedValue(value, ot.ListType(infered_type))
    elif isinstance(value, ov.DictValue):
        infered_key_type = list_type_infer(list(value.get.keys()))
        infered_value_type = list_type_infer(list(value.get.values()))
        if infered_key_type is None or infered_value_type is None:
            raise ParseError(f"Cannot infer type of dict {value}")
        else:
            return DictTypedValue(
                value, ot.DictType(infered_key_type, infered_value_type)
            )


def get_typed_value_with_type(value: ov.Value, vtype: ot.Type) -> TypedValue:
    if isinstance(vtype, ot.VoidType):
        return VoidTypedValue(value, vtype)
    elif isinstance(vtype, ot.BoolType):
        return BoolTypedValue(value, vtype)
    elif isinstance(vtype, ot.IntType):
        return IntTypedValue(value, vtype)
    elif isinstance(vtype, ot.LongType):
        return LongTypedValue(value, vtype)
    elif isinstance(vtype, ot.DoubleType):
        return DoubleTypedValue(value, vtype)
    elif isinstance(vtype, ot.CharType):
        return CharTypedValue(value, vtype)
    elif isinstance(vtype, ot.StringType):
        return StringTypedValue(value, vtype)
    elif isinstance(vtype, ot.OptionalType):
        if isinstance(value, ov.NullValue):
            return VoidTypedValue(value, vtype)
        else:
            tv = get_typed_value_with_type(value, vtype.value_type)
            tv.type = vtype
            return tv
    elif isinstance(vtype, ot.AnyType):
        infered = get_typed_value_without_type(value)
        if not vtype.type_compatible(infered.type):
            raise ParseError(f"{value} is not compatible to `any` type")
        infered.type = vtype
        return infered
    elif isinstance(vtype, ot.ListType):
        return ListTypedValue(value, vtype)
    elif isinstance(vtype, ot.MListType):
        return MListTypedValue(value, vtype)
    elif isinstance(vtype, ot.UnorderedListType):
        return UnorderedListTypedValue(value, vtype)
    elif isinstance(vtype, ot.DictType):
        return DictTypedValue(value, vtype)
    elif isinstance(vtype, ot.MDictType):
        return MDictTypedValue(value, vtype)


def get_typed_value(value: ov.Value, vtype: ot.Type = None) -> TypedValue:
    if vtype is None:
        return get_typed_value_without_type(value)
    else:
        return get_typed_value_with_type(value, vtype)


def align_type(tv: TypedValue, ref_type: ot.Type) -> TypedValue:
    vtype = tv.type
    vval = tv.value
    if not ref_type.type_compatible(vtype):
        raise ParseError(f"Can not align: {vtype} is not compatible to type {ref_type}")
    tv.type = ref_type
    new_ref_type = ref_type
    if isinstance(ref_type, ot.OptionalType):
        new_ref_type = ref_type.value_type
    if isinstance(vval, ov.ListValue):
        assert isinstance(new_ref_type, ot.VType)
        for item in vval.get:
            align_type(item, new_ref_type.value_type)
    elif isinstance(vval, ov.DictValue):
        assert isinstance(new_ref_type, ot.KVType)
        for key, val in vval.get.items():
            align_type(key, new_ref_type.key_type)
            align_type(val, new_ref_type.value_type)
    return tv


class TypedValue:
    def __init__(self):
        self.type: ot.Type = None
        self.value: ov.Value = None

    def value(self):
        return self.value.get

    def __str__(self):
        return f"{self.value}:{self.type}"

    def __eq__(self, other):
        if isinstance(other, TypedValue):
            return str(self) == str(other)
        return False

    def __hash__(self):
        return hash(str(self))


class VoidTypedValue(TypedValue):
    def __init__(self, value: ov.Value, vtype: ot.Type = None):
        super().__init__()
        if not isinstance(value, ov.NullValue):
            raise ParseError(f"Type {vtype} must have null value, but found {value}")
        if vtype is None:
            self.type = ot.VoidType()
        else:
            if not vtype.type_compatible(ot.VoidType()):
                raise ParseError("incompatible type for null value")
            self.type = vtype
        self.value = value


class BoolTypedValue(TypedValue):
    def __init__(self, value: ov.Value, vtype: ot.Type = None):
        super().__init__()
        if not isinstance(value, ov.BoolValue):
            raise ParseError(f"Type {vtype} must have bool value, but found {value}")
        if vtype is None:
            self.type = ot.BoolType()
        else:
            if not vtype.type_compatible(ot.BoolType()):
                raise ParseError("incompatible type for bool value")
            self.type = vtype
        self.value = value


class IntTypedValue(TypedValue):
    def __init__(self, value: ov.Value, vtype: ot.Type = None):
        super().__init__()
        if not isinstance(value, ov.IntValue):
            raise ParseError(f"Type {vtype} must have int value, but found {value}")
        if vtype is None:
            self.type = ot.IntType()
        else:
            if not vtype.type_compatible(ot.IntType()):
                raise ParseError("incompatible type for int value")
            self.type = vtype
        self.value = value


class LongTypedValue(TypedValue):
    def __init__(self, value: ov.Value, vtype: ot.Type = None):
        super().__init__()
        if not isinstance(value, ov.LongValue):
            raise ParseError(f"Type {vtype} must have long value, but found {value}")
        if vtype is None:
            self.type = ot.LongType()
        else:
            if not vtype.type_compatible(ot.LongType()):
                raise ParseError("incompatible type for long value")
            self.type = vtype
        self.value = value


class DoubleTypedValue(TypedValue):
    def __init__(self, value: ov.Value, vtype: ot.Type = None):
        super().__init__()
        if not isinstance(value, ov.DoubleValue):
            raise ParseError(f"Type {vtype} must have double value, but found {value}")
        if vtype is None:
            self.type = ot.DoubleType()
        else:
            if not vtype.type_compatible(ot.DoubleType()):
                raise ParseError("incompatible type for double value")
            self.type = vtype
        self.value = value


class CharTypedValue(TypedValue):
    def __init__(self, value: ov.Value, vtype: ot.Type = None):
        super().__init__()
        if not isinstance(value, ov.CharValue):
            raise ParseError(f"Type {vtype} must have char value, but found {value}")
        if vtype is None:
            self.type = ot.CharType()
        else:
            if not vtype.type_compatible(ot.CharType()):
                raise ParseError("incompatible type for char value")
            self.type = vtype
        self.value = value


class StringTypedValue(TypedValue):
    def __init__(self, value: ov.Value, vtype: ot.Type = None):
        super().__init__()
        if not isinstance(value, ov.StringValue):
            raise ParseError(f"Type {vtype} must have string value, but found {value}")
        if vtype is None:
            self.type = ot.StringType()
        else:
            if not vtype.type_compatible(ot.StringType()):
                raise ParseError("incompatible type for string value")
            self.type = vtype
        self.value = value


class ListTypedValue(TypedValue):
    def __init__(self, value: ov.Value, vtype: ot.Type):
        super().__init__()
        if not isinstance(vtype, ot.ListType):
            raise DebugError("ListTypedValue must be initialized with a ListType")
        if not isinstance(value, ov.ListValue):
            raise ParseError(f"Type {vtype} must have list value, but found {value}")

        items = value.get
        for item in items:
            if not vtype.value_type.type_compatible(item.type):
                raise ParseError(
                    f"List item {item} is not compatible with type {vtype.value_type}"
                )

        self.type = vtype
        self.value = value


class MListTypedValue(TypedValue):
    def __init__(self, value: ov.Value, vtype: ot.Type):
        super().__init__()
        if not isinstance(vtype, ot.MListType):
            raise DebugError("MListTypedValue must be initialized with a MListType")
        if not isinstance(value, ov.ListValue):
            raise ParseError(f"Type {vtype} must have list value, but found {value}")

        items = value.get
        for item in items:
            if not vtype.value_type.type_compatible(item.type):
                raise ParseError(
                    f"List item {item} is not compatible with type {vtype.value_type}"
                )

        self.type = vtype
        self.value = value


class UnorderedListTypedValue(TypedValue):
    def __init__(self, value: ov.Value, vtype: ot.Type):
        super().__init__()
        if not isinstance(vtype, ot.UnorderedListType):
            raise DebugError(
                "UnorderedListTypedValue must be initialized with a UnorderedListType"
            )
        if not isinstance(value, ov.ListValue):
            raise ParseError(f"Type {vtype} must have list value, but found {value}")

        items = value.get
        for item in items:
            if not vtype.value_type.type_compatible(item.type):
                raise ParseError(
                    f"List item {item} is not compatible with type {vtype.value_type}"
                )

        self.type = vtype
        self.value = value


class DictTypedValue(TypedValue):
    def __init__(self, value: ov.Value, vtype: ot.Type):
        super().__init__()
        if not isinstance(vtype, ot.DictType):
            raise DebugError("DictTypedValue must be initialized with a DictType")
        if not isinstance(value, ov.DictValue):
            raise ParseError(f"Type {vtype} must have dict value, but found {value}")

        keys = list(value.get.keys())
        vals = list(value.get.values())

        for key in keys:
            if not vtype.key_type.type_compatible(key.type):
                raise ParseError(
                    f"Dict key {key} is not compatible with type {vtype.key_type}"
                )
        for val in vals:
            if not vtype.value_type.type_compatible(val.type):
                raise ParseError(
                    f"Dict value {val} is not compatible with type {vtype.value_type}"
                )

        self.type = vtype
        self.value = value


class MDictTypedValue(TypedValue):
    def __init__(self, value: ov.Value, vtype: ot.Type):
        super().__init__()
        if not isinstance(vtype, ot.MDictType):
            raise DebugError("MDictTypedValue must be initialized with a MDictType")
        if not isinstance(value, ov.DictValue):
            raise ParseError(f"Type {vtype} must have dict value, but found {value}")

        keys = list(value.get.keys())
        vals = list(value.get.values())

        for key in keys:
            if not vtype.key_type.type_compatible(key.type):
                raise ParseError(
                    f"Mutable Dict key {key} is not compatible with type {vtype.key_type}"
                )
        for val in vals:
            if not vtype.value_type.type_compatible(val.type):
                raise ParseError(
                    f"Mutable Dict value {val} is not compatible with type {vtype.value_type}"
                )

        self.type = vtype
        self.value = value
