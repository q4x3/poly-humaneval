from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.csharp.code_generator_csharp import CodeGeneratorCsharp
from polyeval.plugins.csharp.tests_generator_csharp import TestsGeneratorCsharp
from polyeval.plugins.csharp.naming_generator_csharp import NamingGeneratorCsharp
from polyeval.misc.utils import add_indent


class LangGeneratorCsharp(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorCsharp())
        self.code_genenrator = CodeGeneratorCsharp()
        self.tests_generator = TestsGeneratorCsharp()

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += f"{self.tfs_name}.Append({self.ti_name}{i}());\n"

        result = f"""\
class Program {{
{add_indent(tests_func_str, 1)}
    public static void Main(string[] args) {{
        var {self.tfs_name} = new StringBuilder();
{add_indent(tests_result_str, 2)}
        using (StreamWriter f = new StreamWriter("output.txt")) {{
            f.Write({self.tfs_name}.ToString());
        }}
    }}
}}
"""
        return result
