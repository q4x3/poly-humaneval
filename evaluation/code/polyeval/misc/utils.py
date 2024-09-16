class ParseError(Exception):
    def __init__(self, message):
        super().__init__(message)


class DebugError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ProjectTemplateCreationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ProjectCreationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class EvalError:
    def __init__(self, message):
        super().__init__(message)


def add_indent(text: str, indent: int):
    lines = text.split("\n")
    new_lines = ["    " * indent + line for line in lines]
    return "\n".join(new_lines)


def parse_entry(entry: str):
    names = entry.split(".")
    if len(names) == 1:
        return None, names[0]
    elif len(names) == 2:
        return names[0], names[1]


def to_snake_case(name: str):
    return name


def to_camel_case(name: str):
    words = name.split("_")
    return words[0] + "".join([word.capitalize() for word in words[1:]])


def to_pascal_case(name: str):
    return "".join([word.capitalize() for word in name.split("_")])


def get_naming_function(case: str):
    if case == "snake_case":
        return to_snake_case
    elif case == "camelCase":
        return to_camel_case
    elif case == "PascalCase":
        return to_pascal_case
