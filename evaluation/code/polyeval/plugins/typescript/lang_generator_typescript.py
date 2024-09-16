from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.typescript.code_generator_typescript import (
    CodeGeneratorTypescript,
)
from polyeval.plugins.typescript.tests_generator_typescript import (
    TestsGeneratorTypescript,
)
from polyeval.plugins.typescript.naming_generator_typescript import (
    NamingGeneratorTypescript,
)
from polyeval.misc.utils import add_indent


class LangGeneratorTypescript(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorTypescript())
        self.code_genenrator = CodeGeneratorTypescript()
        self.tests_generator = TestsGeneratorTypescript()

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += f"{self.tfs_name} += {self.ti_name}{i}();\n"

        result = f"""\
{tests_func_str}
const main = () => {{
    let {self.tfs_name} = "";
{add_indent(tests_result_str,1)}
    const f = fs.createWriteStream('output.txt');
    f.write({self.tfs_name});
    f.end();
}}

main();
"""
        return result
