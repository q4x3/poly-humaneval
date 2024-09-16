from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.dart.code_generator_dart import CodeGeneratorDart
from polyeval.plugins.dart.tests_generator_dart import TestsGeneratorDart
from polyeval.plugins.dart.naming_generator_dart import NamingGeneratorDart
from polyeval.misc.utils import add_indent


class LangGeneratorDart(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorDart())
        self.code_genenrator = CodeGeneratorDart()
        self.tests_generator = TestsGeneratorDart()

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += f"{self.tfs_name}.write({self.ti_name}{i}());\n"

        result = f"""\
{tests_func_str}
void main() {{
    var {self.tfs_name} = StringBuffer();
{add_indent(tests_result_str, 1)}
    File f = File('output.txt');
    f.writeAsStringSync({self.tfs_name}.toString());
}}
"""
        return result
