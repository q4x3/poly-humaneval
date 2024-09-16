from __future__ import annotations

from polyeval.misc.utils import get_naming_function


class NamingGeneratorBase:
    global_func_naming = "camelCase"
    global_var_naming = "camelCase"
    member_func_naming = "camelCase"
    member_var_naming = "camelCase"
    arg_naming = "camelCase"
    temp_var_naming = "camelCase"

    def gen_global_func_name(self, name):
        return get_naming_function(self.global_func_naming)(name)

    def gen_global_var_name(self, name):
        return get_naming_function(self.global_var_naming)(name)

    def gen_member_func_name(self, name):
        return get_naming_function(self.member_func_naming)(name)

    def gen_member_var_name(self, name):
        return get_naming_function(self.member_var_naming)(name)

    def gen_temp_var_name(self, name):
        return get_naming_function(self.temp_var_naming)(name)

    def gen_arg_name(self, name):
        return get_naming_function(self.arg_naming)(name)
