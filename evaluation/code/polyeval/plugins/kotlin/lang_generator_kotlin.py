from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.kotlin.code_generator_kotlin import CodeGeneratorKotlin
from polyeval.plugins.kotlin.tests_generator_kotlin import TestsGeneratorKotlin
from polyeval.plugins.kotlin.naming_generator_kotlin import NamingGeneratorKotlin
from polyeval.misc.utils import add_indent


class LangGeneratorKotlin(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorKotlin())
        self.code_genenrator = CodeGeneratorKotlin()
        self.tests_generator = TestsGeneratorKotlin()

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += f"{self.tfs_name}.append({self.ti_name}{i}())\n"

        result = f"""\
{tests_func_str}
fun main() {{
    var {self.tfs_name} = StringBuilder()
{add_indent(tests_result_str, 1)}
    var f = File("output.txt")
    f.writeText({self.tfs_name}.toString())
}}
"""
        return result
