from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.type import *
from polyeval.plugins.rust.naming_generator_rust import NamingGeneratorRust
from polyeval.plugins.rust.type_generator_rust import TypeGeneratorRust
from polyeval.plugins.rust.value_generator_rust import ValueGeneratorRust
from polyeval.objects.problem import (
    TestItem,
    AssignVarCommand,
    GetResultCommand,
    CheckResultCommand,
    CheckNoSideEffectCommand,
)
from polyeval.misc.utils import add_indent


class TestsGeneratorRust(TestsGeneratorBase):
    def __init__(self):
        super().__init__(NamingGeneratorRust())
        self.type_generator = TypeGeneratorRust()
        self.value_generator = ValueGeneratorRust()

    def gen_assign_var_command(self, command: AssignVarCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        with_ref = False
        arg_type = command.value.type
        if isinstance(arg_type, OptionalType):
            if isinstance(arg_type.value_type, (StringType, ListType, DictType, MListType, MDictType, AnyType)):
                with_ref = True
        elif isinstance(arg_type, (StringType, ListType, DictType, MListType, MDictType, AnyType)):
            with_ref = True
        type_str = self.type_generator.gen(arg_type)
        if not with_ref:
            return f"let mut {var_name}: {type_str} = {value_str};\n"
        else:
            return f"""\
let mut {var_name}_unref: {type_str}  = {value_str};
let mut {var_name} = &{var_name}_unref;
"""

    def gen_get_result_command(self, command: GetResultCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        args_str = ", ".join(
            [self.naming_generator.gen_temp_var_name(arg) for arg in command.args]
        )
        func_name = self.naming_generator.gen_global_func_name(command.entry)
        return f"let mut {var_name} = {func_name}({args_str});\n"

    def gen_check_result_command(self, command: CheckResultCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        res_var_name = self.gen_result_var_name()
        result = f"""\
let mut {res_var_name}: {type_str} = {value_str};
{self.os_name}.push_str({var_name}.{self.stf_name}("{command.value.type}").as_str());
{self.es_name}.push_str({res_var_name}.{self.stf_name}("{command.value.type}").as_str());
"""
        return result

    def gen_check_no_side_effect_command(self, command: CheckNoSideEffectCommand):
        var_name = self.naming_generator.gen_temp_var_name(command.var_name)
        value_str = self.value_generator.gen(command.value)
        type_str = self.type_generator.gen(command.value.type)
        res_var_name = self.gen_result_var_name()
        result = f"""\
let mut {res_var_name}: {type_str} = {value_str};
{self.bc_name} = {var_name}.{self.stf_name}("{command.value.type}") + "\\n";
{self.ac_name} = {res_var_name}.{self.stf_name}("{command.value.type}") + "\\n";
{self.ses_name}.push_str(("        Before: ".to_string() + {self.bc_name}.as_str()).as_str());
{self.ses_name}.push_str(("        After: ".to_string() + {self.ac_name}.as_str()).as_str());
"""
        return result

    def gen_test_item(self, idx: int, test_program: TestItem):
        test_name = f"{self.ti_name}{idx}"
        commands_str = ""
        for command in test_program.commands:
            commands_str += self.gen_test_command(command)

        result = f"""\
fn {test_name}() -> String {{
    let mut {self.os_name} = String::new();
    let mut {self.es_name} = String::new();
    let mut {self.ses_name} = String::new();
    let mut {self.bc_name} = String::new();
    let mut {self.ac_name} = String::new();
{add_indent(commands_str, 1)}
    let mut {self.frs_name} = String::new();
    {self.frs_name}.push_str("Test {idx}:\\n");
    {self.frs_name}.push_str(("    Expected: ".to_string() + {self.es_name}.as_str() + "\\n").as_str());
    {self.frs_name}.push_str(("    Output: ".to_string() + {self.os_name}.as_str() + "\\n").as_str());
    {self.frs_name}.push_str(("    Side-Effects: \\n".to_string() + {self.ses_name}.as_str() + "\\n").as_str());
    {self.frs_name}
}}

"""
        return result
