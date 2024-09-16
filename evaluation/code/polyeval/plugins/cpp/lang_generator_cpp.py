from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.cpp.code_generator_cpp import CodeGeneratorCpp
from polyeval.plugins.cpp.tests_generator_cpp import TestsGeneratorCpp
from polyeval.plugins.cpp.naming_generator_cpp import NamingGeneratorCpp
from polyeval.misc.utils import add_indent


class LangGeneratorCpp(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorCpp())
        self.code_genenrator = CodeGeneratorCpp()
        self.tests_generator = TestsGeneratorCpp()

    def gen_solution_header(self):
        code = self.problem.code
        return self.code_genenrator.gen_header_declaration(code)

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += f"{self.tfs_name} += {self.ti_name}{i}();\n"

        result = f"""\
{tests_func_str}
int main() {{
    string {self.tfs_name};
{add_indent(tests_result_str, 1)}
    ofstream f(\"output.txt\");
    if (f.is_open()) {{
        f << {self.tfs_name};
    }}
    return 0;
}}
"""
        return result

    def gen_codes(self):
        code_dict = {
            "main": self.gen_main_code(),
            "target_h": self.gen_solution_header(),
        }
        return code_dict
