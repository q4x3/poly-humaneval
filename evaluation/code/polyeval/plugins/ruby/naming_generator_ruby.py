from __future__ import annotations

from polyeval.generators.base import *
from polyeval.misc.utils import get_naming_function


class NamingGeneratorRuby(NamingGeneratorBase):
    global_func_naming = "snake_case"
    global_var_naming = "snake_case"
    member_func_naming = "snake_case"
    member_var_naming = "snake_case"
    arg_naming = "snake_case"
    temp_var_naming = "snake_case"

    def gen_member_var_name(self, name):
        return "@" + get_naming_function(self.member_var_naming)(name)
