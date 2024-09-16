from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.java.code_generator_java import CodeGeneratorJava
from polyeval.plugins.java.tests_generator_java import TestsGeneratorJava
from polyeval.plugins.java.naming_generator_java import NamingGeneratorJava
from polyeval.misc.utils import add_indent


class LangGeneratorJava(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorJava())
        self.code_genenrator = CodeGeneratorJava()
        self.tests_generator = TestsGeneratorJava()

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += f"{self.tfs_name}.append({self.ti_name}{i}());\n"

        result = f"""\
class Main {{
{add_indent(tests_func_str, 1)}
    public static void main(String[] args) throws Exception {{
        var {self.tfs_name} = new StringBuilder();
{add_indent(tests_result_str, 2)}
        try (FileWriter f = new FileWriter("output.txt")) {{
            f.write({self.tfs_name}.toString());
        }} catch (Exception e) {{
        }}
    }}
}}
"""
        return result
