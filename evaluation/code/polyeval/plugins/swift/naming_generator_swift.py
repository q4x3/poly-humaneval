from __future__ import annotations

from polyeval.generators.base import *


class NamingGeneratorSwift(NamingGeneratorBase):
    global_func_naming = "camelCase"
    global_var_naming = "camelCase"
    member_func_naming = "camelCase"
    member_var_naming = "camelCase"
    arg_naming = "camelCase"
    temp_var_naming = "camelCase"
