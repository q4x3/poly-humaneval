from __future__ import annotations

import os
import shutil
import subprocess

from polyeval.misc.utils import ProjectCreationError
from polyeval.parsing.output_parsing import parse_output
from polyeval.eval.project_template import ProjectTemplate

from enum import Enum

class EvalStatus(Enum):
    CompilationError = 1
    RuntimeError = 2
    OutputError = 3
    Pass = 4


class Project:
    def __init__(self, path, template: ProjectTemplate):
        path = os.path.abspath(path)
        os.makedirs(path)
        self.path = path
        template_path = template.path
        self.srcs = template.srcs

        create_src_paths = [
            os.path.join(template_path, template.srcs[src_name].path)
            for src_name in template.srcs
        ]
        for root, dir, filename in os.walk(template_path, followlinks=True):
            rel_root = os.path.relpath(root, template_path)
            for name in dir:
                os.makedirs(os.path.join(self.path, rel_root, name), exist_ok=True)
            for name in filename:
                full_name = os.path.join(root, name)
                unlink = False
                for src_path in create_src_paths:
                    if os.path.samefile(full_name, src_path):
                        unlink = True
                        break
                if unlink:
                    continue
                os.symlink(full_name, os.path.join(self.path, rel_root, name))

        self.srcs = template.srcs
        self.build_cmd = template.cmds.get("build", None)
        self.run_cmd = template.cmds["run"]

    def set_code(self, name, code):
        if name not in self.srcs:
            raise ProjectCreationError(f"Unknown code file name: {name}")
        src_path = os.path.join(self.path, self.srcs[name].path)
        with open(src_path, "w", encoding="utf-8") as f:
            code = self.srcs[name].code.replace("$$code$$", code)
            f.write(code)

    def set_codes(self, codes: dict[str, str]):
        if set(codes.keys()) != set(self.srcs.keys()):
            raise ProjectCreationError(f"Code file names mismatch")
        for name, code in codes.items():
            self.set_code(name, code)

    def compile(self, timeout=10):
        if self.build_cmd is None:
            return True, "Build not needed"
        try:
            ret = subprocess.run(
                self.build_cmd,
                cwd=self.path,
                timeout=timeout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return True, "Build over"
        except subprocess.SubprocessError as e:
            return False, str(e)

    def run(self, timeout=10):
        try:
            if len(self.run_cmd) == 1 and self.run_cmd[0].startswith("./"):
                if os.path.isfile(os.path.join(self.path, self.run_cmd[0][2:])):
                    executable = os.path.join(self.path, self.run_cmd[0][2:])
                elif os.path.isfile(os.path.join(self.path, self.run_cmd[0][2:] + ".exe")):
                    executable = os.path.join(self.path, self.run_cmd[0][2:] + ".exe")
                else:
                    raise ProjectCreationError(f"Executable {self.run_cmd[0]} not found")
                ret = subprocess.run(
                    executable,
                    cwd=self.path,
                    timeout=timeout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
            else:
                ret = subprocess.run(
                    self.run_cmd,
                    cwd=self.path,
                    timeout=timeout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
            return True, "Run over"
        except subprocess.SubprocessError as e:
            return False, str(e)

    def check_output(self):
        output_txt_path = os.path.join(self.path, "output.txt")
        if not os.path.exists(output_txt_path):
            return False, "No output.txt"
        try:
            with open(output_txt_path, "r", encoding="utf-8") as f:
                output_lines = f.read()
        except UnicodeDecodeError as e:
            return False, "Output file can't decode"
        res = parse_output(output_lines)
        if res is None:
            return False, "Output format error"
        else:
            exp_out_mismatch = False
            side_effect_error = False
            for test in res:
                expected_output_pairs = test[0]
                side_effect_pairs = test[1]
                for pair in expected_output_pairs:
                    expected, output = pair
                    if expected != output:
                        exp_out_mismatch = True
                for pair in side_effect_pairs:
                    before, after = pair
                    if before != after:
                        side_effect_error = True
            if exp_out_mismatch:
                return False, "Output mismatch"
            elif side_effect_error:
                return False, "Side-effect error"
            else:
                return True, "All Passed!"

    def read_output(self):
        output_txt_path = os.path.join(self.path, "output.txt")
        try:
            with open(output_txt_path, "r", encoding="utf-8") as f:
                output = f.read()
            return output
        except UnicodeDecodeError as e:
            return None

    def delete_folder(self):
        shutil.rmtree(self.path)

    def evaluate(self, compile_timeout=10, run_timeout=10, keep_after_eval=False, keep_when_fail=False) -> (
    EvalStatus, str):
        build_stat, msg = self.compile(timeout=compile_timeout)
        if not build_stat:
            ret_stat, msg = EvalStatus.CompilationError, msg
        else:
            run_stat, msg = self.run(timeout=run_timeout)
            if not run_stat:
                ret_stat, msg = EvalStatus.RuntimeError, msg
            else:
                output_stat, msg = self.check_output()
                if not output_stat:
                    ret_stat, msg = EvalStatus.OutputError, msg
                else:
                    ret_stat, msg = EvalStatus.Pass, "All Passed!"
        if keep_after_eval:
            pass
        elif not keep_after_eval and keep_when_fail:
            if ret_stat == EvalStatus.Pass:
                self.delete_folder()
        else:
            self.delete_folder()

        return ret_stat, msg
