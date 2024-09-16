from __future__ import annotations

import os

import yaml
import subprocess
from yaml import CLoader

from polyeval.misc.utils import ProjectTemplateCreationError

class SourceInfo:
    def __init__(self):
        self.path = None
        self.code = None

class ProjectTemplate:
    def __init__(self, path):
        path = os.path.abspath(path)
        self.path = path
        self.srcs = {}
        self.cmds = {}

        yaml_path = os.path.join(path, "polyeval_config.yaml")
        self.load_config(yaml_path)

        res = self.install()
        if not res:
            raise ProjectTemplateCreationError(
                "Install failed. Please check the dependencies."
            )

    def install(self):
        if "install" not in self.cmds:
            return True
        install_command = self.cmds["install"]
        try:
            subprocess.run(install_command, cwd=self.path, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, check=True)
            return True
        except subprocess.SubprocessError as e:
            return False

    def load_config(self, path):
        if not os.path.exists(path):
            raise ProjectTemplateCreationError(f"Config file {path} does not exist")
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.load(f, Loader=CLoader)
        if "sources" not in config:
            raise ProjectTemplateCreationError(
                "Config file should have 'sources' field"
            )
        if "commands" not in config:
            raise ProjectTemplateCreationError(
                "Config file should have 'commands' field"
            )
        for src_id, src_path in config["sources"].items():
            self.srcs[src_id] = SourceInfo()
            self.srcs[src_id].path = os.path.join(src_path)

            whole_src_path = os.path.join(self.path, src_path)
            with open(whole_src_path, "r", encoding="utf-8") as f:
                code = f.read()
                if code.count("$$code$$") != 1:
                    raise ProjectTemplateCreationError(
                        "Source file should have one and only one '$$code$$' placeholder"
                    )
                self.srcs[src_id].code = code

        for command_name, command in config["commands"].items():
            assert command_name in [
                "install",
                "build",
                "run",
            ], f"Unknown command {command_name}"
            if command_name in self.cmds:
                raise ProjectTemplateCreationError(
                    f"Command {command_name} already exists"
                )
            self.cmds[command_name] = command.split()

        if "run" not in self.cmds:
            raise ProjectTemplateCreationError("Config file should have 'run' command")