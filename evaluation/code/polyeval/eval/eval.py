import os
import shutil

from typing import Dict

from polyeval.eval.project import Project
from polyeval.eval.project_template import ProjectTemplate
from polyeval.objects.problem import Problem
from polyeval.generators import create_generator


def gen_codes(lang: str, problem: Problem, target_code: str):
    generator = create_generator(lang, problem)
    codes = generator.gen_codes()
    codes["target"] = target_code
    return codes


def gen_codes_for_single_file(lang: str, problem: Problem, target_code: str):
    generator = create_generator(lang, problem)
    codes = generator.gen_codes()
    main_code = target_code + "\n\n" + codes["main"]
    return {"main": main_code}


def create_project(template: ProjectTemplate, name: str, codes: Dict[str, str], root: str = "./.polyeval",
                   overwrite: bool = False):
    root = os.path.join(root)
    target_dir_name = os.path.join(root, name)
    if overwrite and os.path.exists(target_dir_name):
        shutil.rmtree(target_dir_name)
    project = Project(target_dir_name, template)
    project.set_codes(codes)
    return project
