from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.go.code_generator_go import CodeGeneratorGo
from polyeval.plugins.go.tests_generator_go import TestsGeneratorGo
from polyeval.plugins.go.naming_generator_go import NamingGeneratorGo
from polyeval.misc.utils import add_indent


class LangGeneratorGo(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorGo())
        self.code_genenrator = CodeGeneratorGo()
        self.tests_generator = TestsGeneratorGo()

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += f"{self.tfs_name}.WriteString({self.ti_name}{i}())\n"

        result = f"""\
{tests_func_str}
func main() {{
    var {self.tfs_name} strings.Builder
{add_indent(tests_result_str, 1)}
    f, _ := os.Create("output.txt")
    f.WriteString({self.tfs_name}.String())
    f.Close()
}}
"""
        return result
