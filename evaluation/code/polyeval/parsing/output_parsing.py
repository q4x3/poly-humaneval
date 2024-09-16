from __future__ import annotations
import pyparsing as pyp

pyp_output = None


def get_pyp_output():
    global pyp_output
    if pyp_output is not None:
        return pyp_output
    test_start_line = pyp.Suppress("Test") + pyp.Word(pyp.nums) + pyp.Suppress(":")
    expected_line = pyp.Suppress("Expected:") + pyp.restOfLine
    output_line = pyp.Suppress("Output:") + pyp.restOfLine
    expected_line.set_parse_action(lambda t: t[0].strip())
    output_line.set_parse_action(lambda t: t[0].strip())
    expected_and_output_line = expected_line + output_line
    expected_and_output_line.set_parse_action(lambda t: (t[0], t[1]))

    side_effects_line = pyp.Suppress("Side-Effects:")
    before_line = pyp.Suppress("Before:") + pyp.restOfLine
    after_line = pyp.Suppress("After:") + pyp.restOfLine

    before_line.set_parse_action(lambda t: t[0].strip())
    after_line.set_parse_action(lambda t: t[0].strip())
    before_and_after_line = before_line + after_line
    before_and_after_line.set_parse_action(lambda t: (t[0], t[1]))

    side_effects_group = side_effects_line + pyp.Group(
        pyp.ZeroOrMore(before_and_after_line)
    )
    side_effects_group.set_parse_action(lambda t: list(t[0]))

    test_group = (
        test_start_line
        + pyp.Group(expected_and_output_line)
        + pyp.Group(side_effects_group)
    )
    test_group.set_parse_action(lambda t: (list(t[1]), list(t[2])))

    tests_output = pyp.OneOrMore(test_group)
    tests_output.set_parse_action(lambda t: list(t))

    pyp_output = tests_output

    return tests_output


def parse_output(output: str):
    try:
        return list(get_pyp_output().parseString(output, parse_all=True))
    except pyp.ParseException as e:
        return None
