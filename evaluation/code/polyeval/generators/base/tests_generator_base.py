from __future__ import annotations

from polyeval.generators.base.naming_generator_base import NamingGeneratorBase
from polyeval.objects.problem import (
    TestItem,
    TestCommand,
    AssignVarCommand,
    GetResultCommand,
    CheckResultCommand,
    CheckNoSideEffectCommand,
)


class TestsGeneratorBase:
    def __init__(self, naming_generator=None):
        self.naming_generator = (
            naming_generator if naming_generator is not None else NamingGeneratorBase()
        )
        self.os_name = self.naming_generator.gen_temp_var_name("output_string")
        self.es_name = self.naming_generator.gen_temp_var_name("expected_string")
        self.ses_name = self.naming_generator.gen_temp_var_name("side_effect_string")
        self.bc_name = self.naming_generator.gen_temp_var_name("before_calling")
        self.ac_name = self.naming_generator.gen_temp_var_name("after_calling")
        self.frs_name = self.naming_generator.gen_temp_var_name("final_string_result")
        self.stf_name = self.naming_generator.gen_global_func_name("my_stringify")
        self.ti_name = self.naming_generator.gen_global_func_name("test_item")

        self.res_counter = 0

    def gen_result_var_name(self):
        result = self.naming_generator.gen_temp_var_name(f"result{self.res_counter}")
        self.res_counter += 1
        return result

    def gen_test_command(self, command: TestCommand):
        if isinstance(command, AssignVarCommand):
            return self.gen_assign_var_command(command)
        elif isinstance(command, GetResultCommand):
            return self.gen_get_result_command(command)
        elif isinstance(command, CheckResultCommand):
            return self.gen_check_result_command(command)
        elif isinstance(command, CheckNoSideEffectCommand):
            return self.gen_check_no_side_effect_command(command)

    def gen_assign_var_command(self, command: AssignVarCommand):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_get_result_command(self, command: GetResultCommand):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_check_result_command(self, command: CheckResultCommand):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_check_no_side_effect_command(self, command: CheckNoSideEffectCommand):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_test_item(self, idx: int, test_program: TestItem):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen(self, tests: list[TestItem]):
        results = []
        for idx, test_program in enumerate(tests):
            results.append(self.gen_test_item(idx, test_program))
        return "".join(results)
