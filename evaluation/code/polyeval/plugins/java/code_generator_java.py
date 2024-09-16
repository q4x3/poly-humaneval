from __future__ import annotations

from polyeval.generators.base import *
from polyeval.plugins.java.type_generator_java import TypeGeneratorJava
from polyeval.plugins.java.naming_generator_java import NamingGeneratorJava
from polyeval.misc.utils import add_indent
from polyeval.objects.problem import Function


class CodeGeneratorJava(CodeGeneratorBase):
    def __init__(self):
        super().__init__()
        self.naming_generator = NamingGeneratorJava()
        self.type_generator = TypeGeneratorJava()

    def gen_global_func_prompt(self, func: Function):
        func_name = self.naming_generator.gen_global_func_name(func.name)
        args_names = [
            self.naming_generator.gen_arg_name(arg_name) for arg_name in func.arg_names
        ]
        args_types = [self.type_generator.gen(arg_type) for arg_type in func.arg_types]
        return_type = self.type_generator.gen(func.return_type)
        args_str = ", ".join(
            [
                f"{arg_type} {arg_name}"
                for arg_name, arg_type in zip(args_names, args_types)
            ]
        )
        return f"public static {return_type} {func_name}({args_str}) {{\n    // Implementation here\n}}\n\n"

    def gen_prompt(self, code: dict[str, dict[str, Function]]):
        prompt_str = self.gen_all_global_func_prompt(code)
        result = f"""\
class Global {{
{add_indent(prompt_str, 1)}
}}
"""
        return result.rstrip()