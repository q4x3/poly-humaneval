from __future__ import annotations
import pyparsing as pyp
from polyeval.objects.type import (
    VoidType,
    IntType,
    LongType,
    DoubleType,
    BoolType,
    CharType,
    StringType,
    AnyType,
    ListType,
    MListType,
    UnorderedListType,
    DictType,
    MDictType,
    OptionalType,
)

pyp_type = None


def get_pyp_type():
    global pyp_type
    if pyp_type is not None:
        return pyp_type
    data_type = pyp.Forward()
    subtype_start_tok = pyp.Suppress("<")
    subtype_end_tok = pyp.Suppress(">")
    delim = pyp.Suppress(",")

    # primitive types

    void_type = pyp.Suppress("void")
    int_type = pyp.Suppress("int")
    long_type = pyp.Suppress("long")
    double_type = pyp.Suppress("double")
    char_type = pyp.Suppress("char")
    bool_type = pyp.Suppress("bool")
    string_type = pyp.Suppress("string")
    any_type = pyp.Suppress("any")

    void_type.set_parse_action(lambda t: VoidType())
    int_type.set_parse_action(lambda t: IntType())
    long_type.set_parse_action(lambda t: LongType())
    double_type.set_parse_action(lambda t: DoubleType())
    char_type.set_parse_action(lambda t: CharType())
    bool_type.set_parse_action(lambda t: BoolType())
    string_type.set_parse_action(lambda t: StringType())
    any_type.set_parse_action(lambda t: AnyType())

    # list types
    list_type = pyp.Suppress("list") + subtype_start_tok + data_type + subtype_end_tok
    mlist_type = pyp.Suppress("mlist") + subtype_start_tok + data_type + subtype_end_tok
    unorderedlist_type = (
        pyp.Suppress("unorderedlist") + subtype_start_tok + data_type + subtype_end_tok
    )

    list_type.set_parse_action(lambda t: ListType(t[0]))
    mlist_type.set_parse_action(lambda t: MListType(t[0]))
    unorderedlist_type.set_parse_action(lambda t: UnorderedListType(t[0]))
    #
    # dict types
    dict_type = (
        pyp.Suppress("dict")
        + subtype_start_tok
        + data_type
        + delim
        + data_type
        + subtype_end_tok
    )
    mdict_type = (
        pyp.Suppress("mdict")
        + subtype_start_tok
        + data_type
        + delim
        + data_type
        + subtype_end_tok
    )

    dict_type.set_parse_action(lambda t: DictType(t[0], t[1]))
    mdict_type.set_parse_action(lambda t: MDictType(t[0], t[1]))

    non_optional_type = (
        list_type
        | mlist_type
        | unorderedlist_type
        | dict_type
        | mdict_type
        | any_type
        | void_type
        | int_type
        | long_type
        | double_type
        | char_type
        | bool_type
        | string_type
    )

    # optional type
    optional_type = (
        pyp.Suppress("optional")
        + subtype_start_tok
        + non_optional_type
        + subtype_end_tok
    )
    optional_type_sugar = non_optional_type + pyp.Suppress("?")
    optional_type = optional_type | optional_type_sugar

    optional_type.set_parse_action(lambda t: OptionalType(t[0]))

    data_type << (optional_type | non_optional_type)

    pyp_type = data_type

    return data_type


def type_parsing(s: str):
    data_type = get_pyp_type().parse_string(s, parse_all=True)
    return data_type[0]
