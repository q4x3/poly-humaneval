from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.swift.code_generator_swift import CodeGeneratorSwift
from polyeval.plugins.swift.tests_generator_swift import TestsGeneratorSwift
from polyeval.plugins.swift.naming_generator_swift import NamingGeneratorSwift
from polyeval.misc.utils import add_indent


class LangGeneratorSwift(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorSwift())
        self.code_genenrator = CodeGeneratorSwift()
        self.tests_generator = TestsGeneratorSwift()

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += f"{self.tfs_name}.append({self.ti_name}{i}())\n"

        result = f"""\
{tests_func_str}
func main() {{
    var {self.tfs_name} = ""
{add_indent(tests_result_str, 1)}
    do {{
        try {self.tfs_name}.write(toFile: "output.txt", atomically: true, encoding: .utf8)
    }} catch {{
    }}
}}

main()
"""
        return result
