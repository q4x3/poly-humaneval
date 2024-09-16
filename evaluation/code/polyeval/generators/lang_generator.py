from __future__ import annotations
import importlib
from typing import Type
from polyeval.generators.base import LangGeneratorBase
from polyeval.generators.python import generator_class as python_generator_class
from polyeval.objects.problem import Problem


def get_generator_class(lang: str) -> Type[LangGeneratorBase]:
    if lang == "python":
        return python_generator_class
    plugin_package_name = f"polyeval.plugins.{lang}"
    plugin_package = importlib.import_module(plugin_package_name)
    if hasattr(plugin_package, "generator_class"):
        return plugin_package.generator_class
    else:
        raise ValueError(f"No generator for {lang} found")


def create_generator(lang: str, problem: Problem) -> LangGeneratorBase:
    return get_generator_class(lang)(problem)