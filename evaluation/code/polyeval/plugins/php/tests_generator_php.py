from __future__ import annotations

from polyeval.generators.base import *
from polyeval.plugins.php.naming_generator_php import (
    NamingGeneratorPhp,
)
from polyeval.plugins.php.value_generator_php import (
    ValueGeneratorPhp,
)
from polyeval.objects.problem import (
    TestItem,
    AssignVarCommand,
    GetResultCommand,
    CheckResultCommand,
    CheckNoSideEffectCommand,
)
from polyeval.misc.utils import add_indent


class TestsGeneratorPhp(TestsGeneratorBase):
    def __init__(self):
        super().__init__(NamingGeneratorPhp())
        self.value_generator = ValueGeneratorPhp()

    def gen_assign_var_command(self, command: AssignVarCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        return f"{var_name} = {value_str};\n"

    def gen_get_result_command(self, command: GetResultCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        args_str = ", ".join(
            [self.naming_generator.gen_temp_var_name(arg) for arg in command.args]
        )
        func_name = self.naming_generator.gen_global_func_name(command.entry)
        return f"{var_name} = {func_name}({args_str});\n"

    def gen_check_result_command(self, command: CheckResultCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        res_var_name = self.gen_result_var_name()
        result = f"""\
{res_var_name} = {value_str};
{self.os_name} .= {self.stf_name}({var_name}, "{command.value.type}");
{self.es_name} .= {self.stf_name}({res_var_name}, "{command.value.type}");
"""
        return result

    def gen_check_no_side_effect_command(self, command: CheckNoSideEffectCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        res_var_name = self.gen_result_var_name()
        result = f"""\
{res_var_name} = {value_str};
{self.bc_name} = {self.stf_name}({var_name}, "{command.value.type}") . "\\n";
{self.ac_name} = {self.stf_name}({res_var_name}, "{command.value.type}") . "\\n";
{self.ses_name} .= "        Before: " . {self.bc_name};
{self.ses_name} .= "        After: " . {self.ac_name};
"""
        return result

    def gen_test_item(self, idx: int, test_program: TestItem):
        test_name = f"{self.ti_name}{idx}"
        commands_str = ""
        for command in test_program.commands:
            commands_str += self.gen_test_command(command)

        result = f"""\
function {test_name} () {{
    {self.os_name} = "";
    {self.es_name} = "";
    {self.ses_name} = "";
    {self.bc_name} = "";
    {self.ac_name} = "";
{add_indent(commands_str, 1)}
    {self.frs_name} = "Test {idx}:\\n";
    {self.frs_name} .= "    Expected: " . {self.es_name} . "\\n";
    {self.frs_name} .= "    Output: " . {self.os_name} . "\\n";
    {self.frs_name} .= "    Side-Effects: \\n" . {self.ses_name} . "\\n";
    return {self.frs_name};
}}

"""
        return result
