from polyeval.parsing import parse
from polyeval.eval import ProjectTemplate, EvalStatus, gen_codes, gen_codes_for_single_file, create_project

from tqdm import tqdm
import sys
import os
import argparse
import json

from pebble import ProcessPool

from typing import List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

langs = ["cpp", "csharp", "dart", "go", "java", "javascript", "kotlin", 
           "php", "python", "ruby", "rust", "scala", "swift", "typescript"]

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
parser.add_argument("--input", type=str, default=None)
parser.add_argument("--output", type=str, default="./output_data/result.json")

args = parser.parse_args()
input_file = args.input
output_file = args.output



print(f"Loading problem description and solution...")
with open(os.path.join(ROOT, "./data/poly_humaneval.testdsl"), "r") as f:
    desc_str = f.read()
    problems = parse(desc_str)
with open(os.path.join(ROOT, input_file), "r") as f:
    solutions = json.load(f)

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
    p_name = problem.name.replace("/", "_") + "_" + lang
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

results = {}

with ProcessPool(max_workers=10) as pool:
    futures = []
    for src_lang in solutions:
        for tgt_lang in solutions[src_lang]:
            assert len(solutions[src_lang][tgt_lang]) == 164
            for i in range(164):
                solution = solutions[src_lang][tgt_lang][i]
                problem = list(problems.values())[i]
                name = f"{src_lang}-{tgt_lang}-{i}"
                future = pool.schedule(evaluate, args=[tgt_lang, problem, solution, templates[tgt_lang], fallback_templates[tgt_lang]], timeout=150)
                futures.append([src_lang, tgt_lang, i, future])
    
    for src_lang, tgt_lang, i, future in tqdm(futures):
        try:
            ret = future.result()
            if src_lang not in results:
                results[src_lang] = {}
            if tgt_lang not in results[src_lang]:
                results[src_lang][tgt_lang] = [None for _ in range(164)]
            results[src_lang][tgt_lang][i] = ret
        except Exception as e:
            print(e)
            results[src_lang][tgt_lang][i] = False


with open(output_file, "w") as f:
    json.dump(results, f, indent=4)