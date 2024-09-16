from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.problem import Problem
from polyeval.plugins.ruby.code_generator_ruby import CodeGeneratorRuby
from polyeval.plugins.ruby.tests_generator_ruby import TestsGeneratorRuby
from polyeval.plugins.ruby.naming_generator_ruby import NamingGeneratorRuby
from polyeval.misc.utils import add_indent


class LangGeneratorRuby(LangGeneratorBase):
    def __init__(self, problem: Problem):
        super().__init__(problem, NamingGeneratorRuby())
        self.code_genenrator = CodeGeneratorRuby()
        self.tests_generator = TestsGeneratorRuby()

    def gen_main_code(self):
        tests_func_str = self.gen_tests()
        tests_result_str = ""
        for i in range(len(self.problem.tests)):
            tests_result_str += f"{self.tfs_name} += {self.ti_name}{i}()\n"

        result = f"""\
{tests_func_str}
def main()
    {self.tfs_name} = ""
{add_indent(tests_result_str,1)}
    File.open("output.txt", "w", encoding: 'utf-8') do |f|
        f.write({self.tfs_name})
    end
end

main()
"""
        return result
