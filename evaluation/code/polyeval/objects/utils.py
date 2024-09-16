from __future__ import annotations

from polyeval.misc.unrecommended_literals import get_unrecommended_literals
from polyeval.misc.utils import ParseError
import polyeval.objects.type as ot


def check_good_var_name(name: str):
    bad_names = get_unrecommended_literals()
    if name in bad_names:
        raise ParseError(
            f"Name `{name}` for variables, function or function arguments is not recommended"
        )


def check_good_arg_type(data_type: ot.Type):
    if isinstance(data_type, ot.UnorderedListType):
        raise ParseError(
            f"Data type `{data_type}` is not recommended for function arguments"
        )
    else:
        if isinstance(data_type, ot.KVType):
            check_good_arg_type(data_type.key_type)
        if isinstance(data_type, ot.VType):
            check_good_arg_type(data_type.value_type)


def check_good_return_type(data_type: ot.Type):
    if isinstance(data_type, ot.MListType) or isinstance(data_type, ot.MDictType):
        raise ValueError(f"Data type `{data_type}` is not recommended for return type")
    else:
        if isinstance(data_type, ot.KVType):
            check_good_return_type(data_type.key_type)
        if isinstance(data_type, ot.VType):
            check_good_return_type(data_type.value_type)
