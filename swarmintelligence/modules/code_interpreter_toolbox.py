import json
import sys
import subprocess
import traceback
from io import StringIO

class InterpreterToolbox:
    """
    Herramienta para ejecutar código Python o comandos bash en un agente OpenAI.

    Esta clase sigue la filosofía de "tool que contiene varias sub-tools":
    - python_exec: Ejecuta código Python con captura de stdout y errores
    - bash_exec: Ejecuta comandos bash con subprocess
    """

    def __init__(self, python_executable="python", shell_executable="/bin/bash"):
        self.toolbox_name = 'interpreter_toolbox'
        # Configuración de ejecutables
        self.python_executable = python_executable
        self.shell_executable = shell_executable

        # Sub-herramientas
        self.sub_tools = {
            "python": self._run_python,
            "bash": self._run_bash
        }

        # Configuración de herramientas
        self.tools_config = {
            "python": {
                "name": "python_exec",
                "description": "Ejecuta código Python y devuelve stdout y errores",
                "arguments": {
                    "code": {
                        "type": "string",
                        "description": "Código Python a ejecutar"
                    }
                },
                "required": ["code"]
            },
            "bash": {
                "name": "bash_exec",
                "description": "Ejecuta comandos bash usando subprocess",
                "arguments": {
                    "command": {
                        "type": "string",
                        "description": "Comando bash a ejecutar"
                    }
                },
                "required": ["command"]
            }
        }

    def _run_python(self, code):
        """Ejecuta código Python capturando stdout y errores con traceback completo."""
        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()

        try:
            exec(code)
            return {"output": buffer.getvalue(), "error": ""}
        except Exception:
            return {
                "output": buffer.getvalue(),
                "error": traceback.format_exc()
            }
        finally:
            sys.stdout = old_stdout

    def _run_bash(self, command):
        """Ejecuta comandos bash usando subprocess."""
        try:
            completed = subprocess.run(
                [self.shell_executable, "-c", command],
                capture_output=True,
                text=True
            )
            return {
                "output": completed.stdout,
                "error": completed.stderr if completed.stderr else ""
            }
        except Exception as e:
            return {"output": "", "error": str(e)}

    def initialize(self):
        """
        Devuelve todas las sub-herramientas como herramientas individuales
        para el framework de OpenAI function calling.
        """
        tools = []
        for tool_key, config in self.tools_config.items():
            tool_config = {
                "type": "function",
                "function": {
                    "name": config["name"],
                    "description": config["description"],
                    "parameters": {
                        "type": "object",
                        "properties": config["arguments"],
                        "required": config["required"]
                    }
                }
            }
            tools.append(tool_config)
        return tools

    def call(self, tool_name, payload):
        """
        Ejecuta la sub-herramienta específica con los argumentos proporcionados.
        """
        # Mapeo entre nombres y funciones
        name_to_func = {
            "python_exec": "python",
            "bash_exec": "bash"
        }

        func_key = name_to_func.get(tool_name)
        if not func_key:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({"error": f"Herramienta '{tool_name}' no encontrada"})
            }

        try:
            result = self.sub_tools[func_key](**payload)
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(result, ensure_ascii=False)
            }

        except Exception:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({"error": traceback.format_exc()})
            }

if __name__ == "__main__":
    # Ejemplo de uso de InterpreterTool

    executable = 'C:/Users/AlejandroPrendesCabo/Desktop/proyectos/swarm-intelligence/.venv/Scripts/python.exe'
    bash_executable = 'C:/Program Files/Git/bin/bash.exe'
    tool = InterpreterToolbox(python_executable=executable, shell_executable=bash_executable)

    print("=== Ejemplo 1: Python ===")
    payload1 = {"code": "print('Hola mundo')\nprint(2+3)"}
    response1 = tool.call("python_exec", payload1)
    print("Respuesta:", response1)

    print("\n=== Ejemplo 2: Python con error ===")
    payload2 = {"code": "x = 10/0"}
    response2 = tool.call("python_exec", payload2)
    print("Respuesta:", response2)

    print("\n=== Ejemplo 3: Bash ===")
    payload3 = {"command": "echo 'Archivos:' && ls -1 | head -3"}
    response3 = tool.call("bash_exec", payload3)
    print("Respuesta:", response3)

    print("\n=== Ejemplo 4: Bash con error ===")
    payload4 = {"command": "ls /ruta/inexistente"}
    response4 = tool.call("bash_exec", payload4)
    print("Respuesta:", response4)

    print("\n=== Configuración de herramientas para OpenAI ===")
    tools_config = tool.initialize()
    print(json.dumps(tools_config, indent=2, ensure_ascii=False))
