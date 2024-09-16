from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.rust.code_generator_rust import CodeGeneratorRust
from polyeval.plugins.rust.tests_generator_rust import TestsGeneratorRust
from polyeval.plugins.rust.naming_generator_rust import NamingGeneratorRust
from polyeval.misc.utils import add_indent


class LangGeneratorRust(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorRust())
        self.code_genenrator = CodeGeneratorRust()
        self.tests_generator = TestsGeneratorRust()

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += (
                f"{self.tfs_name}.push_str({self.ti_name}{i}().as_str());\n"
            )

        result = f"""\
{tests_func_str}
fn main() {{
    let mut {self.tfs_name} = String::new();
{add_indent(tests_result_str, 1)}
    let mut f = File::create("output.txt").expect("Create Failed");
    f.write_all({self.tfs_name}.as_bytes());
}}
"""
        return result
