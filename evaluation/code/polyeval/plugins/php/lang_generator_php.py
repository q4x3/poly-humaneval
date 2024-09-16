from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.php.code_generator_php import CodeGeneratorPhp
from polyeval.plugins.php.tests_generator_php import TestsGeneratorPhp
from polyeval.plugins.php.naming_generator_php import NamingGeneratorPhp
from polyeval.misc.utils import add_indent


class LangGeneratorPhp(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorPhp())
        self.code_genenrator = CodeGeneratorPhp()
        self.tests_generator = TestsGeneratorPhp()

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += f"{self.tfs_name} .= {self.ti_name}{i}();\n"

        result = f"""\
{tests_func_str}
function main() {{
    {self.tfs_name} = "";
{add_indent(tests_result_str,1)}
    $f = fopen("output.txt", "w");
    fwrite($f, {self.tfs_name});
    fclose($f);
}}

main();
"""
        return result
