import os

from polyeval.parsing import parse
from polyeval.eval import ProjectTemplate, gen_codes_for_single_file, create_project

description = """
problem HumanEval/4 {
    code {
        func mean_absolute_deviation(numbers:list<double>) -> double
    }
    tests {
        template nse {
            ([1.0, 2.0, 3.0]) -> 0.666666667
            ([1.0, 2.0, 3.0, 4.0]) -> 1.0
            ([1.0, 2.0, 3.0, 4.0, 5.0]) -> 1.2
        }
    }
}
"""

solution = """
def mean_absolute_deviation(numbers: List[float]) -> float:
    mean = sum(numbers) / len(numbers)
    return sum([abs(x - mean) for x in numbers]) / len(numbers)
"""

problems = parse(description)
template_path = "./project-templates/default/python"
template = ProjectTemplate(template_path)
codes = gen_codes_for_single_file(lang="python", problem=list(problems.values())[0], target_code=solution)
proj = create_project(template=template, name="example", codes=codes, root=".polyeval/", overwrite=True)
ret_stat, msg = proj.evaluate(compile_timeout=10, run_timeout=10, keep_after_eval=True)
print(ret_stat)
print(proj.read_output())