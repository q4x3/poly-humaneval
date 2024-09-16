from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.scala.code_generator_scala import CodeGeneratorScala
from polyeval.plugins.scala.tests_generator_scala import TestsGeneratorScala
from polyeval.plugins.scala.naming_generator_scala import NamingGeneratorScala
from polyeval.misc.utils import add_indent


class LangGeneratorScala(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorScala())
        self.code_genenrator = CodeGeneratorScala()
        self.tests_generator = TestsGeneratorScala()

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += f"{self.tfs_name} ++= {self.ti_name}{i}()\n"

        result = f"""\
{tests_func_str}
@main def main = {{
    var {self.tfs_name} = new StringBuilder()
{add_indent(tests_result_str, 1)}
    var f = new FileWriter("output.txt")
    try {{
        f.write({self.tfs_name}.result())
    }} finally {{
        f.close()
    }}
}}
"""
        return result
