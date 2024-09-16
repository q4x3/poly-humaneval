from __future__ import annotations

from polyeval.generators.base import *
from polyeval.plugins.javascript.type_generator_javascript import (
    TypeGeneratorJavascript,
)
from polyeval.plugins.javascript.naming_generator_javascript import (
    NamingGeneratorJavascript,
)
from polyeval.objects.problem import Function


class CodeGeneratorJavascript(CodeGeneratorBase):
    def __init__(self):
        super().__init__()
        self.naming_generator = NamingGeneratorJavascript()
        self.type_generator = TypeGeneratorJavascript()

    def gen_global_func_prompt(self, func: Function):
        func_name = self.naming_generator.gen_global_func_name(func.name)
        args_names = [
            self.naming_generator.gen_arg_name(arg_name) for arg_name in func.arg_names
        ]
        args_types = [self.type_generator.gen(arg_type) for arg_type in func.arg_types]
        return_type = self.type_generator.gen(func.return_type)

        doc_str_params = "".join(
            f" * @param {{{arg_type}}} {arg_name}\n"
            for arg_name, arg_type in zip(args_names, args_types)
        )
        doc_str = f"""\
/**
{doc_str_params}\
 * @returns {{{return_type}}}
 */
"""
        args_str = ", ".join(args_names)
        return f"{doc_str}export const {func_name} = ({args_str}) => {{\n    // Implementation here\n}}\n\n"
    def gen_prompt(self, code: dict[str, dict[str, Function]]):
        return self.gen_all_global_func_prompt(code).rstrip()
