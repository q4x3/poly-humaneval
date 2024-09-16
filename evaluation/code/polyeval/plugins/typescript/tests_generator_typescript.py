from __future__ import annotations

from polyeval.generators.base import *
from polyeval.plugins.typescript.naming_generator_typescript import (
    NamingGeneratorTypescript,
)
from polyeval.plugins.typescript.type_generator_typescript import (
    TypeGeneratorTypescript,
)
from polyeval.plugins.typescript.value_generator_typescript import (
    ValueGeneratorTypescript,
)
from polyeval.objects.problem import (
    TestItem,
    AssignVarCommand,
    GetResultCommand,
    CheckResultCommand,
    CheckNoSideEffectCommand,
)
from polyeval.misc.utils import add_indent


class TestsGeneratorTypescript(TestsGeneratorBase):
    def __init__(self):
        super().__init__(NamingGeneratorTypescript())
        self.type_generator = TypeGeneratorTypescript()
        self.value_generator = ValueGeneratorTypescript()

    def gen_assign_var_command(self, command: AssignVarCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        return f"let {var_name}: {type_str} = {value_str};\n"

    def gen_get_result_command(self, command: GetResultCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        args_str = ", ".join(
            [self.naming_generator.gen_temp_var_name(arg) for arg in command.args]
        )
        func_name = self.naming_generator.gen_global_func_name(command.entry)
        return f"// @ts-ignore\nlet {var_name} = {func_name}({args_str});\n"

    def gen_check_result_command(self, command: CheckResultCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        res_var_name = self.gen_result_var_name()
        result = f"""\
let {res_var_name}: {type_str} = {value_str};
{self.os_name} += {self.stf_name}({var_name}, "{command.value.type}");
{self.es_name} += {self.stf_name}({res_var_name}, "{command.value.type}");
"""
        return result

    def gen_check_no_side_effect_command(self, command: CheckNoSideEffectCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        res_var_name = self.gen_result_var_name()
        result = f"""\
let {res_var_name}: {type_str} = {value_str};
{self.bc_name} = {self.stf_name}({var_name}, "{command.value.type}") + "\\n";
{self.ac_name} = {self.stf_name}({res_var_name}, "{command.value.type}") + "\\n";
{self.ses_name} += "        Before: " + {self.bc_name};
{self.ses_name} += "        After: " + {self.ac_name};
"""
        return result

    def gen_test_item(self, idx: int, test_program: TestItem):
        test_name = f"{self.ti_name}{idx}"
        commands_str = ""
        for command in test_program.commands:
            commands_str += self.gen_test_command(command)

        result = f"""\
const {test_name} = () => {{
    let {self.os_name} = "";
    let {self.es_name} = "";
    let {self.ses_name} = "";
    let {self.bc_name} = "";
    let {self.ac_name} = "";
{add_indent(commands_str, 1)}
    let {self.frs_name} = "Test {idx}:\\n";
    {self.frs_name} += "    Expected: " + {self.es_name} + "\\n";
    {self.frs_name} += "    Output: " + {self.os_name} + "\\n";
    {self.frs_name} += "    Side-Effects: \\n" + {self.ses_name} + "\\n";
    return {self.frs_name};
}}

"""
        return result
