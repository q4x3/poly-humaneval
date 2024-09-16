from __future__ import annotations

from polyeval.generators.base import *
from polyeval.plugins.scala.naming_generator_scala import NamingGeneratorScala
from polyeval.plugins.scala.type_generator_scala import TypeGeneratorScala
from polyeval.plugins.scala.value_generator_scala import ValueGeneratorScala
from polyeval.objects.problem import (
    TestItem,
    AssignVarCommand,
    GetResultCommand,
    CheckResultCommand,
    CheckNoSideEffectCommand,
)
from polyeval.misc.utils import add_indent


class TestsGeneratorScala(TestsGeneratorBase):
    def __init__(self):
        super().__init__(NamingGeneratorScala())
        self.type_generator = TypeGeneratorScala()
        self.value_generator = ValueGeneratorScala()

    def gen_assign_var_command(self, command: AssignVarCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        return f"var {var_name}: {type_str} = {value_str}\n"

    def gen_get_result_command(self, command: GetResultCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        args_str = ", ".join(
            [self.naming_generator.gen_temp_var_name(arg) for arg in command.args]
        )
        func_name = self.naming_generator.gen_global_func_name(command.entry)
        return f"var {var_name} = {func_name}({args_str})\n"

    def gen_check_result_command(self, command: CheckResultCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        res_var_name = self.gen_result_var_name()
        result = f"""\
var {res_var_name}: {type_str} = {value_str}
{self.os_name} ++= {self.stf_name}({var_name}, "{command.value.type}")
{self.es_name} ++= {self.stf_name}({res_var_name}, "{command.value.type}")
"""
        return result

    def gen_check_no_side_effect_command(self, command: CheckNoSideEffectCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        res_var_name = self.gen_result_var_name()
        result = f"""\
var {res_var_name}: {type_str} = {value_str}
{self.bc_name} = {self.stf_name}({var_name}, "{command.value.type}") + "\\n"
{self.ac_name} = {self.stf_name}({res_var_name}, "{command.value.type}") + "\\n"
{self.ses_name} ++= "        Before: " + {self.bc_name}
{self.ses_name} ++= "        After: " + {self.ac_name}
"""
        return result

    def gen_test_item(self, idx: int, test_program: TestItem):
        test_name = f"{self.ti_name}{idx}"
        commands_str = ""
        for command in test_program.commands:
            commands_str += self.gen_test_command(command)

        result = f"""\
def {test_name}(): String = {{
    var {self.os_name} = StringBuilder()
    var {self.es_name} = StringBuilder()
    var {self.ses_name} = StringBuilder()
    var {self.bc_name} = ""
    var {self.ac_name} = ""
{add_indent(commands_str, 1)}
    var {self.frs_name} = StringBuilder()
    {self.frs_name} ++= "Test {idx}:\\n"
    {self.frs_name} ++= "    Expected: " + {self.es_name}.toString() + "\\n"
    {self.frs_name} ++= "    Output: " + {self.os_name}.toString() + "\\n"
    {self.frs_name} ++= "    Side-Effects: \\n" + {self.ses_name}.toString() + "\\n"
    {self.frs_name}.result()
}}

"""
        return result
