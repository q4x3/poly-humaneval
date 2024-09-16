from __future__ import annotations

from polyeval.generators.base import *
from polyeval.plugins.csharp.naming_generator_csharp import NamingGeneratorCsharp
from polyeval.plugins.csharp.type_generator_csharp import TypeGeneratorCsharp
from polyeval.plugins.csharp.value_generator_csharp import ValueGeneratorCsharp
from polyeval.objects.problem import (
    TestItem,
    AssignVarCommand,
    GetResultCommand,
    CheckResultCommand,
    CheckNoSideEffectCommand,
)
from polyeval.misc.utils import add_indent


class TestsGeneratorCsharp(TestsGeneratorBase):
    def __init__(self):
        super().__init__(NamingGeneratorCsharp())
        self.type_generator = TypeGeneratorCsharp()
        self.value_generator = ValueGeneratorCsharp()

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
        return f"var {var_name} = {func_name}({args_str});\n"

    def gen_check_result_command(self, command: CheckResultCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        res_var_name = self.gen_result_var_name()
        result = f"""\
{type_str} {res_var_name} = {value_str};
{self.os_name}.Append({self.stf_name}({var_name}, "{command.value.type}"));
{self.es_name}.Append({self.stf_name}({res_var_name}, "{command.value.type}"));
"""
        return result

    def gen_check_no_side_effect_command(self, command: CheckNoSideEffectCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        res_var_name = self.gen_result_var_name()
        result = f"""\
{type_str} {res_var_name} = {value_str};
{self.bc_name} = {self.stf_name}({var_name}, "{command.value.type}") + "\\n";
{self.ac_name} = {self.stf_name}({res_var_name}, "{command.value.type}") + "\\n";
{self.ses_name}.Append("        Before: " + {self.bc_name});
{self.ses_name}.Append("        After: " + {self.ac_name});
"""
        return result

    def gen_test_item(self, idx: int, test_program: TestItem):
        test_name = f"{self.ti_name}{idx}"
        commands_str = ""
        for command in test_program.commands:
            commands_str += self.gen_test_command(command)

        result = f"""\
public static string {test_name}() {{
    var {self.os_name} = new StringBuilder();
    var {self.es_name} = new StringBuilder();
    var {self.ses_name} = new StringBuilder();
    string {self.bc_name} = "";
    string {self.ac_name} = "";
{add_indent(commands_str, 1)}
    var {self.frs_name} = new StringBuilder("Test {idx}:\\n");
    {self.frs_name}.Append("    Expected: " + {self.es_name}.ToString() + "\\n");
    {self.frs_name}.Append("    Output: " + {self.os_name}.ToString() + "\\n");
    {self.frs_name}.Append("    Side-Effects: \\n" + {self.ses_name}.ToString() + "\\n");
    return {self.frs_name}.ToString();
}}

"""
        return result
