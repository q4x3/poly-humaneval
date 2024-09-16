from polyeval.parsing import parse
from polyeval.eval import ProjectTemplate, EvalStatus, gen_codes, gen_codes_for_single_file, create_project

from tqdm import tqdm
import sys
import os
import argparse
import json

from typing import List

from pebble import ProcessPool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# langs = ["cpp", "csharp", "dart", "go", "java", "javascript", "kotlin", 
#            "php", "python", "ruby", "rust", "scala", "swift", "typescript"]

langs = ["cpp", "csharp", "dart", "go", "java", "javascript", "kotlin", "php", "python", "ruby", "rust", "scala", "typescript"]

suffix = {
    "cpp": "cpp",
    "csharp": "cs",
    "dart": "dart",
    "go": "go",
    "java": "java",
    "javascript": "js",
    "kotlin": "kt",
    "php": "php",
    "python": "py",
    "ruby": "rb",
    "rust": "rs",
    "scala": "scala",
    "swift": "swift",
    "typescript": "ts"
}

cur_langs = langs

parser = argparse.ArgumentParser()
parser.add_argument("--lang", type=str, default=None)
parser.add_argument("--idx", type=int, nargs="+", default=None)

args = parser.parse_args()
if args.lang is not None:
    if args.lang not in langs:
        raise Exception(f"Language not supported: {args.lang}")
    cur_langs = [args.lang]

print(f"Loading problem description and solution...")
with open(os.path.join(ROOT, "./data/poly_humaneval.testdsl"), "r") as f:
    desc_str = f.read()
    problems = parse(desc_str)
with open(os.path.join(ROOT, "./data/poly_humaneval_sol.json"), "r") as f:
    solutions = json.load(f)

idxs = list(range(0, len(problems)))
if args.idx is not None:
    idxs = args.idx
    if len(idxs) == 1:
        idxs = [idxs[0]]
    elif len(idxs) == 2:
        idxs = list(range(idxs[0], idxs[1] + 1))
    else:
        raise Exception("args error")



print(f"Loading project templates...")
templates = {}
fallback_templates = {}
for lang in cur_langs:
    print(f"Loading {lang} ...")
    templates[lang] = ProjectTemplate(os.path.join(ROOT, "./project-templates/default", lang))
    if os.path.exists(os.path.join(ROOT, "./project-templates/with-dependencies", lang)):
        print(f"Loading {lang} with dependencies ...")
        fallback_templates[lang] = ProjectTemplate(os.path.join(ROOT, "./project-templates/with-dependencies", lang))
    else:
        fallback_templates[lang] = None


def evaluate(lang, problem, solution, template, fallback_template):
    p_name = problem.name.replace("/", "_")
    codes = gen_codes_for_single_file(lang=lang, problem=problem, target_code=solution)
    proj = create_project(template, f"{lang}-{p_name}-sf", codes,
                                      root=os.path.join(ROOT, ".polyeval/"), overwrite=True)
    ret_stat, msg = proj.evaluate(compile_timeout=10, run_timeout=10)
    if ret_stat == EvalStatus.Pass:
        return True
    if fallback_template is not None:
        codes = gen_codes(lang=lang, problem=problem, target_code=solution)
        proj = create_project(fallback_template, f"{lang}-{p_name}", codes, root=os.path.join(ROOT, ".polyeval/"), overwrite=True)
        ret_stat, msg = proj.evaluate(compile_timeout=30, run_timeout=10)
        if ret_stat == EvalStatus.Pass:
            return True
    return False


with ProcessPool(max_workers=10) as pool:
    futures = []
    for lang in cur_langs:
        for idx in tqdm(idxs):
            problem = list(problems.values())[idx]
            solution = solutions[lang][problem.name]
            future = pool.schedule(evaluate, args=[lang, problem, solution, templates[lang], fallback_templates[lang]], timeout=90)
            futures.append([lang, idx, future])
    
    for lang, idx, future in tqdm(futures):
        try:
            ret = future.result()
            if not ret:
                print(f"{lang}-{idx} failed")
        except TimeoutError as error:
            print(f"{lang}-{idx} failed")

