import traceback
import io
import contextlib
import json
import subprocess
import os

class CodeInterpreterToolClass:
    def __init__(self, interpreter_path, path_folders):
        self.interpreter_path = interpreter_path
        self.path_folders = path_folders
        self.name = "code_interpreter"
        self.description = "Code interpreter for expert software development in the environment of the project."
        self.args = [
            {
                "name": "programming_language", "type": "string",
                "enum": ["python", "bash"],
                "description": "Language of the code to execute.",
                "required": True,
            },
            {
                "name": "code", "type": "string",
                "description": "Code that will be executed in the code interpreter.",
                "required": True,
            },
        ]

    def initialize(self):
        pass

    def get_tool_dict(self):
        tool_name = self.name
        tool_description = self.description
        tool_args = self.args
        args_schema = {}
        required = []
        for arg in tool_args:
            args_schema[arg["name"]] = {
                "type": arg["type"],
                "description": arg["description"],
            }
            if arg.get("required"):
                required.append(arg["name"])
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": args_schema,
                    "required": required,
                },
            },
        }

    def run(self, programming_language='python', code='print("Hello World")'):
        if programming_language == 'python':
            try:
                stdout_buffer = io.StringIO()
                stderr_buffer = io.StringIO()
                with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                    env = os.environ.copy()
                    env["PYTHONPATH"] = os.pathsep.join(self.path_folders)
                    env["PYTHONUNBUFFERED"] = "1"
                    response = subprocess.run([self.interpreter_path, "-c", code], text=True, capture_output=True, env=env)
                result = response.stdout
                error = response.stderr or None
            except Exception:
                result = None
                error = traceback.format_exc()
        else:
            completed = subprocess.run(code, shell=True, capture_output=True, text=True)
            result = completed.stdout
            error = completed.stderr or None
        return json.dumps({"result": result, "error": error}, indent=2)

