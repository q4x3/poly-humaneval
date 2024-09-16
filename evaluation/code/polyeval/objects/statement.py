from __future__ import annotations

import json
import polyeval.objects.type as ot
import polyeval.objects.typed_value as tv


class Statement:
    def __init__(self):
        pass

    def __str__(self):
        raise NotImplementedError("This method must be implemented by a subclass")


class ProblemStatement(Statement):
    def __init__(
        self,
        problem_name: str,
        children: list[InfoStatement | CodeStatement | TestsStatement],
    ):
        super().__init__()
        self.name = problem_name
        self.children = children

    def __str__(self):
        text = "Problem " + self.name + "\n"
        text += "".join([str(child) for child in self.children])
        return text


class InfoStatement(Statement):
    def __init__(self, children: list[InfoItemStatement]):
        super().__init__()
        self.children = children

    def __str__(self):
        text = "\tInfo\n"
        text += "".join([str(child) for child in self.children])
        return text


class InfoItemStatement(Statement):
    def __init__(self, name: str, value: str):
        super().__init__()
        self.name = name
        self.value = json.loads(value)

    def __str__(self):
        return f"\t\t{self.name}: {json.dumps(self.value)}\n"


class CodeStatement(Statement):
    def __init__(self, children: list[FuncStatement]):
        super().__init__()
        self.children = children

    def __str__(self):
        text = "\tCode\n"
        text += "".join([str(child) for child in self.children])
        return text


class FuncStatement(Statement):
    class FuncArg:
        def __init__(self, name: str, data_type: ot.Type):
            self.name = name
            self.data_type = data_type

        def __str__(self):
            return f"{self.name}: {self.data_type}"

    def __init__(self, name: str, args: list[FuncArg], return_type: ot.Type):
        super().__init__()
        self.name = name
        self.args = args
        self.return_type = return_type

    def __str__(self):
        args_str = ", ".join([str(arg) for arg in self.args])
        return f"\t\tfunc {self.name}({args_str}) -> {self.return_type}\n"


class TestsStatement(Statement):
    def __init__(self, items: list[TestItemStatement]):
        super().__init__()
        self.items = items

    def __str__(self):
        text = "\tTests\n"
        text += "".join([str(item) for item in self.items])
        return text


class TestItemStatement(Statement):
    def __init__(self):
        super().__init__()

    def __str__(self):
        raise NotImplementedError("This method must be implemented by a subclass")


class TestTemplateStatement(TestItemStatement):
    def __init__(self):
        super().__init__()

    def __str__(self):
        raise NotImplementedError("This method must be implemented by a subclass")


class IgnoreSideEffectTemplateStatement(TestTemplateStatement):
    def __init__(self, items: list[TestTemplateItemStatement], entry=None):
        super().__init__()
        self.entry = entry
        self.items = items

    def __str__(self):
        text = f"\t\tIgnoreSideEffect entry:{self.entry}\n"
        text += "".join([str(item) for item in self.items])
        return text


class NoSideEffectTemplateStatement(TestTemplateStatement):
    def __init__(self, items: list[TestTemplateItemStatement], entry=None):
        super().__init__()
        self.entry = entry
        self.items = items

    def __str__(self):
        text = f"\t\tNoSideEffect entry:{self.entry}\n"
        text += "".join([str(item) for item in self.items])
        return text


class TestTemplateItemStatement(Statement):
    def __init__(self, args: list[tv.TypedValue], expected: tv.TypedValue):
        super().__init__()
        self.args = args
        self.expected = expected

    def __str__(self):
        args_str = ", ".join([str(arg) for arg in self.args])
        return f"\t\t\t{args_str} -> {self.expected}\n"
