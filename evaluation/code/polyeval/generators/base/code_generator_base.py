from __future__ import annotations

from polyeval.objects.problem import Function
class CodeGeneratorBase:
    def __init__(self):
        pass

    def gen_global_func_prompt(self, func: Function):
        raise NotImplementedError("This method must be implemented by a subclass")

    def gen_all_global_func_prompt(self, code: dict[str, dict[str, Function]]):
        global_funcs = code["global"]
        result = ""
        for name, func in global_funcs.items():
            result += self.gen_global_func_prompt(func)
        return result.rstrip()

    def gen_prompt(self, code: dict[str, dict[str, Function]]):
        return self.gen_all_global_func_prompt(code).rstrip()
