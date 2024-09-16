from __future__ import annotations

from polyeval.generators.base import *


class NamingGeneratorCsharp(NamingGeneratorBase):
    global_func_naming = "PascalCase"
    global_var_naming = "camelCase"
    member_func_naming = "PascalCase"
    member_var_naming = "camelCase"
    arg_naming = "camelCase"
    temp_var_naming = "camelCase"
