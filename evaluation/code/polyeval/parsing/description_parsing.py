from __future__ import annotations
import pyparsing as pyp
from polyeval.parsing.type_parsring import get_pyp_type
from polyeval.parsing.value_parsing import get_pyp_value
from polyeval.objects.statement import (
    FuncStatement,
    CodeStatement,
    TestsStatement,
    TestTemplateItemStatement,
    NoSideEffectTemplateStatement,
    IgnoreSideEffectTemplateStatement,
    InfoItemStatement,
    InfoStatement,
    ProblemStatement,
)
from polyeval.objects.problem import Problems

pyp_desc_code = None
pyp_desc_tests = None
pyp_desc = None


def get_pyp_desc_code():
    global pyp_desc_code
    if pyp_desc_code is not None:
        return pyp_desc_code
    else:
        data_type = get_pyp_type()
        func_name = pyp.Word(pyp.alphas.lower(), pyp.alphanums.lower() + "_")
        arg_name = pyp.Word(pyp.alphas.lower(), pyp.alphanums.lower() + "_")
        func_arg = arg_name + pyp.Suppress(":") + data_type
        func_arg.set_parse_action(lambda t: FuncStatement.FuncArg(t[0], t[1]))
        func = (
            pyp.Suppress("func")
            + func_name
            + pyp.Suppress("(")
            + pyp.Group(pyp.Optional(pyp.delimitedList(func_arg)))
            + pyp.Suppress(")")
            + pyp.Suppress("->")
            + data_type
        )
        func.set_parse_action(lambda t: FuncStatement(t[0], t[1], t[2]))
        desc_code = (
            pyp.Suppress("code")
            + pyp.Suppress("{")
            + pyp.Group(pyp.ZeroOrMore(func))
            + pyp.Suppress("}")
        )
        desc_code.set_parse_action(lambda t: CodeStatement(t[0]))
        pyp_desc_code = desc_code
        return desc_code


def get_pyp_desc_tests():
    global pyp_desc_tests
    if pyp_desc_tests is not None:
        return pyp_desc_tests
    else:
        data_value = get_pyp_value()
        test_template_item = (
            pyp.Suppress("(")
            + pyp.Group(pyp.Optional(pyp.delimitedList(data_value)))
            + pyp.Suppress(")")
            + pyp.Suppress("->")
            + data_value
        )
        test_template_item.set_parse_action(
            lambda t: TestTemplateItemStatement(t[0], t[1])
        )
        test_template_items = pyp.Group(pyp.ZeroOrMore(test_template_item))
        test_template_items.set_parse_action(lambda t: list(t))

        entry_name = pyp.Word(pyp.alphas, pyp.alphanums.lower() + "_.")
        nse_template_statement = (
            pyp.Suppress("template")
            + (pyp.Suppress("no_side_effect") | pyp.Suppress("nse"))
            + pyp.Optional(pyp.Suppress("entry") + entry_name, None)
            + pyp.Suppress("{")
            + test_template_items
            + pyp.Suppress("}")
        )

        ise_template_statement = (
            pyp.Suppress("template")
            + (pyp.Suppress("ignore_side_effect") | pyp.Suppress("ise"))
            + pyp.Optional(pyp.Suppress("entry") + entry_name, None)
            + pyp.Suppress("{")
            + test_template_items
            + pyp.Suppress("}")
        )

        nse_template_statement.set_parse_action(
            lambda t: NoSideEffectTemplateStatement(t[1], t[0])
        )
        ise_template_statement.set_parse_action(
            lambda t: IgnoreSideEffectTemplateStatement(t[1], t[0])
        )

        desc_tests = (
            pyp.Suppress("tests")
            + pyp.Suppress("{")
            + pyp.Group(pyp.ZeroOrMore(nse_template_statement | ise_template_statement))
            + pyp.Suppress("}")
        )

        desc_tests.set_parse_action(lambda t: TestsStatement(t[0]))
        pyp_desc_tests = desc_tests
        return desc_tests


def get_pyp_desc():
    global pyp_desc
    if pyp_desc is not None:
        return pyp_desc
    else:
        desc_code = get_pyp_desc_code()
        desc_tests = get_pyp_desc_tests()

        info_name = pyp.Word(pyp.alphas, pyp.alphanums + "_" + "-")
        info_item_statement = (
            info_name
            + pyp.Suppress("=")
            + pyp.QuotedString(
                quoteChar='"',
                escChar="\\",
                unquoteResults=False,
                multiline=True,
                convertWhitespaceEscapes=False,
            )
        )
        info_item_statement.set_parse_action(lambda t: InfoItemStatement(t[0], t[1]))

        desc_info = (
            pyp.Suppress("info")
            + pyp.Suppress("{")
            + pyp.Group(pyp.ZeroOrMore(info_item_statement))
            + pyp.Suppress("}")
        )

        desc_info.set_parse_action(lambda t: InfoStatement(t[0]))

        problem_name = pyp.Word(pyp.alphanums + "/_-.")
        problem_statement = (
            pyp.Suppress("problem")
            + problem_name
            + pyp.Suppress("{")
            + pyp.Group(pyp.ZeroOrMore(desc_info | desc_code | desc_tests))
            + pyp.Suppress("}")
        )
        problem_statement.set_parse_action(lambda t: ProblemStatement(t[0], t[1]))

        problems = pyp.Group(pyp.ZeroOrMore(problem_statement))
        problems.set_parse_action(lambda t: t[0])
        pyp_desc = problems
        return problems


def parse(string: str):
    desc = get_pyp_desc().parse_string(string, parse_all=True)
    return Problems(desc).data
