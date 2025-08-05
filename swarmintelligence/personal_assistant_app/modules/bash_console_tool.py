import subprocess
import shlex
import time
import json
import traceback

class PowerShellTimeoutError(Exception):
    """Excepción para timeout de PowerShell"""
    pass

class BashConsoleInterpreterToolClass:
    def __init__(self, timeout_seconds=30):
        self.name = "bash_interpreter"
        self.description = "Executes bash code in the OS console.."
        self.args = [
            {
                'name': 'code_str',
                'type': 'string',
                'description': 'Bash code to execute.',
                'required': True
            }
        ]
        self.timeout_seconds = timeout_seconds

    def initialize(self):
        pass

    def get_tool_dict(self):
        return self._gen_tool_dict(self.name, self.description, self.args)

    def run(self, code_str):
        """
        Ejecuta el código PowerShell y devuelve un JSON con:
        - success: True/False
        - code_output: texto de stdout
        - error / error_type / error_traceback en caso de fallo
        - execution_info: duración y estado
        - warnings: contenido de stderr si existe
        - debug_info: sugerencias basadas en el tipo de error o advertencias
        - code_analysis: análisis básico del script
        """
        # 1) Validación básica
        if not code_str or not code_str.strip():
            return json.dumps({
                "success": False,
                "code_output": "",
                "error": "No se proporcionó código PowerShell",
                "error_type": "ValidationError",
                "execution_info": None,
                "debug_info": {
                    "suggestion": "Proporciona un script PowerShell válido"
                }
            }, indent=2)

        # 2) Preparar ejecución
        start_time = time.time()
        try:
            # Ejecución
            completed = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy", "Bypass",
                    "-Command", code_str
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                shell=False
            )
            end_time = time.time()

            # Resultado base
            result = {
                "success": completed.returncode == 0,
                "code_output": completed.stdout,
                "execution_info": {
                    "duration_seconds": end_time - start_time,
                    "completed": True
                }
            }

            # 3) Errores de PowerShell (returncode != 0)
            if completed.returncode != 0:
                result.update({
                    "error": f"PowerShell finalizó con código {completed.returncode}",
                    "error_type": "PowerShellError",
                    "error_traceback": completed.stderr,
                    "debug_info": {
                        "suggestion": self._get_error_suggestion("PowerShellError", completed.stderr),
                        "common_fixes": self._get_common_fixes("PowerShellError")
                    }
                })
            else:
                result["error"] = None
                result["error_type"] = None

            # 4) Warnings / stderr
            if completed.stderr and completed.returncode == 0:
                result["warnings"] = completed.stderr
                result["debug_info"] = {
                    "note": "La ejecución devolvió advertencias en stderr"
                }

            # 5) Análisis del código
            result["code_analysis"] = self._analyze_code(code_str)

            return json.dumps(result, indent=2)

        except subprocess.TimeoutExpired as e:
            # Timeout
            end_time = time.time()
            result = {
                "success": False,
                "code_output": e.stdout or "",
                "error": f"TIMEOUT: La ejecución excedió los {self.timeout_seconds} segundos",
                "error_type": "TimeoutExpired",
                "execution_info": {
                    "duration_seconds": end_time - start_time,
                    "completed": False
                },
                "debug_info": {
                    "suggestion": f"Optimiza o acorta el script PowerShell para que termine en menos de {self.timeout_seconds}s"
                }
            }
            if e.stderr:
                result["warnings"] = e.stderr
            return json.dumps(result, indent=2)

        except Exception as e:
            # Error inesperado en el propio Python
            end_time = time.time()
            tb = traceback.format_exc()
            result = {
                "success": False,
                "code_output": "",
                "error": str(e),
                "error_type": type(e).__name__,
                "error_traceback": tb,
                "execution_info": {
                    "duration_seconds": end_time - start_time,
                    "completed": False
                },
                "debug_info": {
                    "suggestion": "Revisa la traza de error para más detalles"
                }
            }
            return json.dumps(result, indent=2)

    def _get_error_suggestion(self, error_type, error_message):
        """Sugerencias según tipo de error en PowerShell"""
        base = "Revisa la sintaxis y valida los cmdlets utilizados."
        mapping = {
            "PowerShellError": "Verifica cmdlets, rutas y permisos en el sistema."
        }
        return mapping.get(error_type, base)

    def _get_common_fixes(self, error_type):
        """Sugerencias de arreglos comunes"""
        fixes = {
            "PowerShellError": [
                "Asegúrate de que los cmdlets están disponibles en el sistema",
                "Revisa la ortografía de nombres y rutas",
                "Ejecuta PowerShell con permisos elevados si hace falta"
            ],
            "TimeoutExpired": [
                "Divide el script en partes más pequeñas",
                "Optimiza bucles o consultas",
                "Aumenta el parámetro timeout_seconds si es adecuado"
            ]
        }
        return fixes.get(error_type, ["Revisa la documentación de PowerShell", "Depura paso a paso"])

    def _analyze_code(self, code_str):
        """Análisis ligero del script PowerShell"""
        lines = code_str.splitlines()
        return {
            "line_count": len(lines),
            "has_functions": any(l.strip().lower().startswith("function") for l in lines),
            "has_loops": any(kw in code_str.lower() for kw in ["for ", "foreach ", "while "]),
            "has_conditionals": any(kw in code_str.lower() for kw in ["if(", "if "]),
            "complexity": "simple" if len(lines) < 10 else "moderada" if len(lines) < 50 else "alta"
        }

    def _gen_tool_dict(self, tool_name, tool_description, tool_args):
        """Genera la definición de la herramienta para el agente de IA"""
        args_dict = {}
        required = []
        for a in tool_args:
            args_dict[a['name']] = {
                "type": a['type'],
                "description": a['description']
            }
            if a.get('required'):
                required.append(a['name'])
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": args_dict,
                    "required": required
                }
            }
        }