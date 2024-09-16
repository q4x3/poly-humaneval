from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.generators.python.code_generator_python import CodeGeneratorPython
from polyeval.generators.python.tests_generator_python import TestsGeneratorPython
from polyeval.generators.python.naming_generator_python import NamingGeneratorPython
from polyeval.misc.utils import add_indent


class LangGeneratorPython(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorPython())
        self.code_genenrator = CodeGeneratorPython()
        self.tests_generator = TestsGeneratorPython()

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += f"{self.tfs_name} += {self.ti_name}{i}()\n"

        result = f"""\
{tests_func_str}
def main():
    {self.tfs_name} = ""
{add_indent(tests_result_str, 1)}
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write({self.tfs_name})

if __name__ == "__main__":
    main()
"""
        return result
