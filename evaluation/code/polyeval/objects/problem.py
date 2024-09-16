from __future__ import annotations

import json
from typing import Optional

import polyeval.objects.type as ot
import polyeval.objects.typed_value as tv
import polyeval.objects.statement as os

from polyeval.misc.utils import ParseError
from polyeval.objects.utils import check_good_var_name


class Problems:
    def __init__(self, problems: list[os.ProblemStatement]):
        self.data = {}
        for problem in problems:
            if problem.name in self.data:
                raise ParseError(f"Duplicate problem name: {problem.name}")
            else:
                self.data[problem.name] = Problem(problem)

    def __str__(self):
        text = ""
        for problem in self.data.values():
            text += str(problem)
        return text


class Problem:
    def __init__(self, ps: os.ProblemStatement):
        self.name = ps.name
        self.info = None
        self.code = None
        self.tests = None

        for child_statement in ps.children:
            if isinstance(child_statement, os.InfoStatement):
                if self.info is not None:
                    raise ParseError(f"Problem {ps.name} has multiple info blocks")
                self.info = {}
                for info_item in child_statement.children:
                    if info_item.name in self.info:
                        raise ParseError(
                            f"Info of problem {ps.name} have duplicate info key: {info_item.name}"
                        )
                    else:
                        self.info[info_item.name] = info_item.value
            elif isinstance(child_statement, os.CodeStatement):
                if self.code is not None:
                    raise ParseError(f"Problem {ps.name} has multiple code blocks")
                self.code = {"global": {}}
                for func in child_statement.children:
                    if func.name in self.code["global"]:
                        raise ParseError(
                            f"Code of problem {ps.name} have duplicate function name: {func.name}"
                        )
                    else:
                        self.code["global"][func.name] = Function(func)
            elif isinstance(child_statement, os.TestsStatement):
                if self.tests is not None:
                    raise ParseError(f"Problem {ps.name} has multiple tests blocks")
                self.tests = []
                for test_item in child_statement.items:
                    self.tests += get_test_items(test_item, self.code)

    def __str__(self):
        text = "Problem " + self.name + "\n"
        if self.info is not None:
            text += "\tInfo:\n"
            for name, value in self.info.items():
                text += f"\t\t{name}: {json.dumps(value)}\n"
        if self.code is not None:
            text += "\tCode:\n"
            for name, func in self.code["global"].items():
                text += f"\t\t{func}\n"
            for s_name, s in self.code.items():
                if s_name == "global":
                    continue
                text += f"\t\tStruct {s_name}:\n"
                for name, func in s.items():
                    text += f"\t\t\t{func}\n"
        if self.tests is not None:
            text += "\tTests:\n"
            for idx, test in enumerate(self.tests):
                text += f"\t\tTest {idx}:\n"
                for command in test.commands:
                    text += f"\t\t\t{command}\n"
        return text


def get_test_items(item: os.TestItemStatement, code: dict[str, dict[str, Function]]):
    if isinstance(
        item, (os.IgnoreSideEffectTemplateStatement, os.NoSideEffectTemplateStatement)
    ):
        test_items = []
        entry = item.entry
        target_func: Optional[Function] = None
        if entry is None:
            if len(code["global"]) != 1:
                names = list(code["global"].keys())
                raise ParseError(
                    f"Function entry not specified, but found {len(code['global'])} global functions: {names}"
                )
            target_func = list(code["global"].values())[0]
            entry = target_func.name
        elif "." not in entry:
            if entry not in code["global"]:
                raise ParseError(f"Function {entry} not found")
            target_func = code["global"][entry]
        else:
            module_name, func_name = entry.split(".")
            if module_name not in code:
                raise ParseError(f"Module {module_name} not found")
            if func_name not in code[module_name]:
                raise ParseError(
                    f"Function {func_name} not found in module {module_name}"
                )
            target_func = code[module_name][func_name]
        for item_statement in item.items:
            test_item = TestItem()
            args = item_statement.args
            if len(args) != len(target_func.arg_types):
                raise ParseError(
                    f"Function {target_func.name} expect {len(target_func.arg_types)} arguments, "
                    f"but found {len(args)}"
                )
            arg_names = []
            for i in range(len(args)):
                if not target_func.arg_types[i].type_compatible(args[i].type):
                    raise ParseError(
                        f"Function {target_func.name} argument {i} expect type "
                        f"{target_func.arg_types[i]}, but found not compatible type {args[i].type}"
                    )
                new_arg_value = tv.align_type(args[i], target_func.arg_types[i])
                new_temp_name = target_func.arg_names[i] + "_0"
                test_item.add_command(AssignVarCommand(new_temp_name, new_arg_value))
                arg_names.append(new_temp_name)

            if not target_func.return_type.type_compatible(
                item_statement.expected.type
            ):
                raise ParseError(
                    f"Function {target_func.name} expect return type "
                    f"{target_func.return_type}, but found not compatible type {item_statement.expected.type}"
                )
            test_item.add_command(GetResultCommand("result", arg_names, entry))
            new_expected_value = tv.align_type(
                item_statement.expected, target_func.return_type
            )
            test_item.add_command(CheckResultCommand("result", new_expected_value))

            if isinstance(item, os.NoSideEffectTemplateStatement):
                for i in range(len(args)):
                    new_arg_value = tv.align_type(args[i], target_func.arg_types[i])
                    test_item.add_command(
                        CheckNoSideEffectCommand(arg_names[i], new_arg_value)
                    )
            test_items.append(test_item)
        return test_items


class Function:
    def __init__(self, fs: os.FuncStatement):
        self.name: str = fs.name
        self.arg_names: list[str] = []
        self.arg_types: list[ot.Type] = [arg.data_type for arg in fs.args]
        self.return_type: ot.Type = fs.return_type
        check_good_var_name(fs.name)
        for arg in fs.args:
            if arg.name in self.arg_names:
                raise ParseError(
                    f"Function {fs.name} have duplicate argument name: {arg.name}"
                )
            else:
                check_good_var_name(arg.name)
                self.arg_names.append(arg.name)

    def __str__(self):
        arg_list = [
            arg_name + ":" + str(arg_type)
            for arg_name, arg_type in zip(self.arg_names, self.arg_types)
        ]
        return f"{self.name}({', '.join(arg_list)}) -> {self.return_type}"


class TestItem:
    def __init__(self):
        self.commands: list[TestCommand] = []
        self.temp_vars = []

    def add_command(self, command: TestCommand):
        if isinstance(command, AssignVarCommand):
            if command.var_name in self.temp_vars:
                raise ParseError(f"Variable {command.var_name} already exists")
            self.temp_vars.append(command.var_name)
        elif isinstance(command, GetResultCommand):
            for arg_name in command.args:
                if arg_name not in self.temp_vars:
                    raise ParseError(f"Variable {arg_name} not found")
            if command.var_name in self.temp_vars:
                raise ParseError(f"Variable {command.var_name} already exists")
            self.temp_vars.append(command.var_name)
        elif isinstance(command, CheckResultCommand):
            if command.var_name not in self.temp_vars:
                raise ParseError(f"Variable {command.var_name} not found")
        elif isinstance(command, CheckNoSideEffectCommand):
            if command.var_name not in self.temp_vars:
                raise ParseError(f"Variable {command.var_name} not found")
        self.commands.append(command)


class TestCommand:
    def __init__(self, var_name: str):
        check_good_var_name(var_name)
        self.var_name = var_name
        pass


class AssignVarCommand(TestCommand):
    def __init__(self, var_name: str, value: tv.TypedValue):
        super().__init__(var_name)
        self.value = value

    def __str__(self):
        return f"{self.var_name} = {self.value}"


class GetResultCommand(TestCommand):
    def __init__(self, var_name: str, args: list[str], entry: str):
        super().__init__(var_name)
        self.entry = entry
        self.args = args

    def __str__(self):
        return f"{self.var_name} = {self.entry}({', '.join(self.args)})"


class CheckResultCommand(TestCommand):
    def __init__(self, var_name: str, value: tv.TypedValue):
        super().__init__(var_name)
        self.value = value

    def __str__(self):
        return f"assert {self.var_name} == {self.value}"


class CheckNoSideEffectCommand(TestCommand):
    def __init__(self, var_name: str, value: tv.TypedValue):
        super().__init__(var_name)
        self.value = value

    def __str__(self):
        return f"assert {self.var_name} == {self.value} # side effect"
