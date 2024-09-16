from __future__ import annotations

from polyeval.generators.base import *
from polyeval.plugins.cpp.naming_generator_cpp import NamingGeneratorCpp
from polyeval.plugins.cpp.type_generator_cpp import TypeGeneratorCpp
from polyeval.plugins.cpp.value_generator_cpp import ValueGeneratorCpp
from polyeval.objects.problem import (
    TestItem,
    AssignVarCommand,
    GetResultCommand,
    CheckResultCommand,
    CheckNoSideEffectCommand,
)
from polyeval.misc.utils import add_indent


class TestsGeneratorCpp(TestsGeneratorBase):
    def __init__(self):
        super().__init__(NamingGeneratorCpp())
        self.type_generator = TypeGeneratorCpp()
        self.value_generator = ValueGeneratorCpp()

    def gen_assign_var_command(self, command: AssignVarCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        return f"{type_str} {var_name} = {value_str};\n"

    def gen_get_result_command(self, command: GetResultCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        args_str = ", ".join(
            [self.naming_generator.gen_temp_var_name(arg) for arg in command.args]
        )
        func_name = self.naming_generator.gen_global_func_name(command.entry)
        return f"auto {var_name} = {func_name}({args_str});\n"

    def gen_check_result_command(self, command: CheckResultCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        res_var_name = self.gen_result_var_name()
        result = f"""\
{type_str} {res_var_name} = {value_str};
{self.os_name} += {self.stf_name}({var_name}, string("{command.value.type}"));
{self.es_name} += {self.stf_name}({res_var_name}, string("{command.value.type}"));
"""
        return result

    def gen_check_no_side_effect_command(self, command: CheckNoSideEffectCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        res_var_name = self.gen_result_var_name()
        result = f"""\
{type_str} {res_var_name} = {value_str};
{self.bc_name} = {self.stf_name}({var_name}, string("{command.value.type}")) + string("\\n");
{self.ac_name} = {self.stf_name}({res_var_name}, string("{command.value.type}")) + string("\\n");
{self.ses_name} += string("        Before: ") + {self.bc_name};
{self.ses_name} += string("        After: ") + {self.ac_name};
"""
        return result

    def gen_test_item(self, idx: int, test_program: TestItem):
        test_name = f"{self.ti_name}{idx}"
        commands_str = ""
        for command in test_program.commands:
            commands_str += self.gen_test_command(command)

        result = f"""\
string {test_name}() {{
    string {self.os_name};
    string {self.es_name};
    string {self.ses_name};
    string {self.bc_name};
    string {self.ac_name};
{add_indent(commands_str, 1)}
    string {self.frs_name} = "Test {idx}:\\n";
    {self.frs_name} += string("    Expected: ") + {self.es_name} + string("\\n");
    {self.frs_name} += string("    Output: ") + {self.os_name} + string("\\n");
    {self.frs_name} += string("    Side-Effects: \\n") + {self.ses_name} + string("\\n");
    return {self.frs_name};
}}

"""
        return result
