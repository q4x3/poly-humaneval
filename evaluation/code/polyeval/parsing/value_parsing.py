from __future__ import annotations
import pyparsing as pyp
import polyeval.parsing.type_parsring as tp

from polyeval.objects.value import (
    NullValue,
    IntValue,
    LongValue,
    DoubleValue,
    BoolValue,
    CharValue,
    StringValue,
    ListValue,
    DictValue,
)

from polyeval.objects.typed_value import get_typed_value, TypedValue

pyp_value = None


def get_pyp_value():
    global pyp_value
    if pyp_value is not None:
        return pyp_value
    data_type = tp.get_pyp_type()
    typed_value = pyp.Forward()

    null_literal = pyp.Suppress("null")
    integer_literal = pyp.Combine(pyp.Optional("-") + pyp.Word(pyp.nums)) + ~(
        pyp.FollowedBy("L") | pyp.FollowedBy(".")
    )
    long_literal = pyp.Combine(pyp.Optional("-") + pyp.Word(pyp.nums)) + pyp.Suppress(
        "L"
    )

    double_literal = pyp.Combine(
        pyp.Optional("-") + pyp.Word(pyp.nums) + "." + pyp.Word(pyp.nums)
    )
    nan_literal = pyp.Literal("nan")
    inf_literal = pyp.Combine(pyp.Optional("-") + pyp.Literal("inf"))
    double_literal = nan_literal | inf_literal | double_literal

    char_literal = pyp.QuotedString(
        quoteChar="'",
        escChar="\\",
        unquoteResults=False,
        multiline=True,
        convertWhitespaceEscapes=False,
    )
    bool_literal = pyp.Literal("true") | pyp.Literal("false")
    string_literal = pyp.QuotedString(
        quoteChar='"',
        escChar="\\",
        unquoteResults=False,
        multiline=True,
        convertWhitespaceEscapes=False,
    )

    null_literal.set_parse_action(lambda t: NullValue())
    integer_literal.set_parse_action(lambda t: IntValue(int(t[0])))
    long_literal.set_parse_action(lambda t: LongValue(int(t[0])))
    double_literal.set_parse_action(lambda t: DoubleValue(float(t[0])))
    bool_literal.set_parse_action(lambda t: BoolValue(bool(t[0] == "true")))
    char_literal.set_parse_action(lambda t: CharValue(t[0]))
    string_literal.set_parse_action(lambda t: StringValue(t[0]))

    list_literal = (
        pyp.Suppress("[")
        + pyp.Optional(pyp.delimitedList(typed_value))
        + pyp.Suppress("]")
    )
    kv_pair = typed_value + pyp.Suppress("=>") + typed_value
    dict_literal = (
        pyp.Suppress("{") + pyp.Optional(pyp.delimitedList(kv_pair)) + pyp.Suppress("}")
    )

    list_literal.set_parse_action(lambda t: ListValue(list(t)))
    dict_literal.set_parse_action(lambda t: DictValue(list(t)))

    value = (
        null_literal
        | integer_literal
        | long_literal
        | double_literal
        | bool_literal
        | char_literal
        | string_literal
        | list_literal
        | dict_literal
    )

    typed_value << (value + pyp.Suppress(":") + data_type | value)

    typed_value.set_parse_action(
        lambda t: get_typed_value(t[0], (t[1] if len(t) == 2 else None))
    )

    pyp_value = typed_value

    return typed_value


def value_parsing(s: str) -> TypedValue:
    data_value = get_pyp_value().parse_string(s, parse_all=True)
    return data_value[0]
