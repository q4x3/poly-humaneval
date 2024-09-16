from __future__ import annotations

from polyeval.generators.base import *
from polyeval.objects.type import *
from polyeval.plugins.rust.type_generator_rust import TypeGeneratorRust
from polyeval.plugins.rust.naming_generator_rust import NamingGeneratorRust
from polyeval.objects.problem import Function


class CodeGeneratorRust(CodeGeneratorBase):
    def __init__(self):
        super().__init__()
        self.naming_generator = NamingGeneratorRust()
        self.type_generator = TypeGeneratorRust()

    def gen_func_args(self, arg_type: Type):
        type_str = self.type_generator.gen(arg_type)
        if isinstance(arg_type, OptionalType):
            if isinstance(arg_type.value_type, (StringType, ListType, DictType, AnyType)):
                return f"&{type_str}"
            elif isinstance(arg_type.value_type, (MListType, MDictType)):
                return f"&mut {type_str}"
            else:
                return type_str
        else:
            if isinstance(arg_type, (StringType, ListType, DictType, AnyType)):
                return f"&{type_str}"
            elif isinstance(arg_type, (MListType, MDictType)):
                return f"&mut {type_str}"
            else:
                return type_str
    def gen_global_func_prompt(self, func: Function):
        func_name = self.naming_generator.gen_global_func_name(func.name)
        args_names = [
            self.naming_generator.gen_arg_name(arg_name) for arg_name in func.arg_names
        ]
        args_types = [self.gen_func_args(arg_type) for arg_type in func.arg_types]
        return_type = self.type_generator.gen(func.return_type)
        args_str = ", ".join(
            [
                f"{arg_name}: {arg_type}"
                for arg_name, arg_type in zip(args_names, args_types)
            ]
        )
        return f"pub fn {func_name}({args_str}) -> {return_type} {{\n    // Implementation here\n}}\n\n"

    def gen_prompt(self, code: dict[str, dict[str, Function]]):
        return self.gen_all_global_func_prompt(code).rstrip()