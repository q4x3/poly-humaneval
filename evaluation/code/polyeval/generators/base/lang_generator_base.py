from __future__ import annotations

from polyeval.objects.problem import Problem
from polyeval.generators.base.naming_generator_base import NamingGeneratorBase


class LangGeneratorBase:
    def __init__(self, problem: Problem, naming_generator=None):
        self.problem = problem
        self.naming_generator = (
            naming_generator if naming_generator is not None else NamingGeneratorBase()
        )
        self.code_genenrator = None
        self.tests_generator = None

        self.tfs_name = self.naming_generator.gen_temp_var_name("to_file_str")
        self.ti_name = self.naming_generator.gen_global_func_name("test_item")

    def gen_prompt(self):
        code = self.problem.code
        return self.code_genenrator.gen_prompt(code)

    def gen_tests(self):
        tests = self.problem.tests
        return self.tests_generator.gen(tests)

    def gen_main_code(self):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_codes(self):
        code_dict = {"main": self.gen_main_code()}
        return code_dict
