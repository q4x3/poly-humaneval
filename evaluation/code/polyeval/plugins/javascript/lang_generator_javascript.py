from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.javascript.code_generator_javascript import (
    CodeGeneratorJavascript,
)
from polyeval.plugins.javascript.tests_generator_javascript import (
    TestsGeneratorJavascript,
)
from polyeval.plugins.javascript.naming_generator_javascript import (
    NamingGeneratorJavascript,
)
from polyeval.misc.utils import add_indent


class LangGeneratorJavascript(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorJavascript())
        self.code_genenrator = CodeGeneratorJavascript()
        self.tests_generator = TestsGeneratorJavascript()

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
