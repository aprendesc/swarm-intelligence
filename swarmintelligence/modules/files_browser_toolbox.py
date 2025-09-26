import json
import os
import glob
import traceback
from pathlib import Path

class FilesBrowserToolbox:
    """
    Herramienta para navegación y manipulación de archivos para un agente OpenAI.

    Esta clase integra múltiples sub-herramientas relacionadas con archivos:
    - list: Explorar archivos y carpetas
    - search: Buscar archivos por patrón
    - read: Leer contenido de archivos
    - write: Escribir archivos completos
    - replace: Editar archivos mediante reemplazo de líneas

    Cada sub-herramienta tiene su propio conjunto de argumentos específicos,
    evitando conflictos entre parámetros excluyentes.
    """

    def __init__(self):
        self.toolbox_name = 'files_browser_toolbox'
        # Configuración de sub-herramientas disponibles
        self.sub_tools = {
            "list": self._list_files,
            "search": self._search_files,
            "read": self._read_file,
            "write": self._write_file,
            "replace": self._replace_in_file
        }

        # Configuración base para cada sub-herramienta
        self.tools_config = {
            "list": {
                "name": "files_list",
                "description": "Lista archivos y carpetas en un directorio",
                "arguments": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del directorio a explorar",
                        "default": "."
                    },
                    "show_hidden": {
                        "type": "boolean",
                        "description": "Mostrar archivos ocultos",
                        "default": False
                    }
                },
                "required": []
            },
            "search": {
                "name": "files_search",
                "description": "Busca archivos por patrón de nombre",
                "arguments": {
                    "pattern": {
                        "type": "string",
                        "description": "Patrón de búsqueda (ej: '*.py', 'test*', '**/*.txt')"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directorio base para búsqueda",
                        "default": "."
                    }
                },
                "required": ["pattern"]
            },
            "read": {
                "name": "files_read",
                "description": "Lee el contenido completo de un archivo",
                "arguments": {
                    "file_path": {
                        "type": "string",
                        "description": "Ruta del archivo a leer"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "Codificación del archivo",
                        "default": "utf-8"
                    }
                },
                "required": ["file_path"]
            },
            "write": {
                "name": "files_write",
                "description": "Escribe contenido completo a un archivo",
                "arguments": {
                    "file_path": {
                        "type": "string",
                        "description": "Ruta del archivo a escribir"
                    },
                    "content": {
                        "type": "string",
                        "description": "Contenido a escribir en el archivo"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "Codificación del archivo",
                        "default": "utf-8"
                    }
                },
                "required": ["file_path", "content"]
            },
            "replace": {
                "name": "files_replace",
                "description": "Reemplaza una línea específica en un archivo",
                "arguments": {
                    "file_path": {
                        "type": "string",
                        "description": "Ruta del archivo a editar"
                    },
                    "old_line": {
                        "type": "string",
                        "description": "Línea exacta a reemplazar"
                    },
                    "new_line": {
                        "type": "string",
                        "description": "Nueva línea de reemplazo"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "Codificación del archivo",
                        "default": "utf-8"
                    }
                },
                "required": ["file_path", "old_line", "new_line"]
            }
        }

    def _list_files(self, path=".", show_hidden=False):
        """Lista archivos y carpetas en un directorio."""
        try:
            path = Path(path)
            if not path.exists():
                return {"error": f"La ruta '{path}' no existe"}

            if not path.is_dir():
                return {"error": f"La ruta '{path}' no es un directorio"}

            items = []
            for item in path.iterdir():
                if not show_hidden and item.name.startswith('.'):
                    continue

                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "path": str(item)
                })

            # Ordenar: directorios primero, luego archivos
            items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))

            return {
                "action": "list",
                "path": str(path.absolute()),
                "items": items,
                "count": len(items),
                "error": ""
            }

        except Exception as e:
            return {"action": "list", "error": traceback.format_exc()}

    def _search_files(self, pattern, path="."):
        """Busca archivos por patrón de nombre."""
        try:
            search_path = Path(path)
            if not search_path.exists():
                return {"error": f"La ruta base '{path}' no existe"}

            # Usar glob para búsqueda de patrones
            if search_path.is_dir():
                search_pattern = str(search_path / pattern)
            else:
                search_pattern = pattern

            matches = glob.glob(search_pattern, recursive=True)

            files = []
            for match in matches:
                match_path = Path(match)
                files.append({
                    "name": match_path.name,
                    "type": "directory" if match_path.is_dir() else "file",
                    "path": str(match_path.absolute()),
                    "size": match_path.stat().st_size if match_path.is_file() else None
                })

            return {
                "action": "search",
                "pattern": pattern,
                "base_path": str(search_path.absolute()),
                "matches": files,
                "count": len(files),
                "error": ""
            }

        except Exception as e:
            return {"action": "search", "error": traceback.format_exc()}

    def _read_file(self, file_path, encoding="utf-8"):
        """Lee el contenido completo de un archivo."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"El archivo '{file_path}' no existe"}

            if not path.is_file():
                return {"error": f"La ruta '{file_path}' no es un archivo"}

            with open(path, 'r', encoding=encoding) as f:
                content = f.read()

            return {
                "action": "read",
                "file_path": str(path.absolute()),
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines()),
                "encoding": encoding,
                "error": ""
            }

        except Exception as e:
            return {"action": "read", "error": traceback.format_exc()}

    def _write_file(self, file_path, content, encoding="utf-8"):
        """Escribe contenido completo a un archivo."""
        try:
            path = Path(file_path)

            # Crear directorios padre si no existen
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding=encoding) as f:
                f.write(content)

            return {
                "action": "write",
                "file_path": str(path.absolute()),
                "bytes_written": len(content.encode(encoding)),
                "lines_written": len(content.splitlines()),
                "encoding": encoding,
                "error": ""
            }

        except Exception as e:
            return {"action": "write", "error": traceback.format_exc()}

    def _replace_in_file(self, file_path, old_line, new_line, encoding="utf-8"):
        """Reemplaza una línea específica en un archivo."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"El archivo '{file_path}' no existe"}

            if not path.is_file():
                return {"error": f"La ruta '{file_path}' no es un archivo"}

            # Leer el archivo
            with open(path, 'r', encoding=encoding) as f:
                lines = f.readlines()

            # Buscar y reemplazar la línea
            replacements_made = 0
            for i, line in enumerate(lines):
                if line.rstrip() == old_line.rstrip():
                    lines[i] = new_line + '\n' if not new_line.endswith('\n') else new_line
                    replacements_made += 1

            if replacements_made == 0:
                return {"error": f"No se encontró la línea '{old_line}' en el archivo"}

            # Escribir el archivo modificado
            with open(path, 'w', encoding=encoding) as f:
                f.writelines(lines)

            return {
                "action": "replace",
                "file_path": str(path.absolute()),
                "old_line": old_line,
                "new_line": new_line,
                "replacements_made": replacements_made,
                "total_lines": len(lines),
                "encoding": encoding,
                "error": ""
            }

        except Exception as e:
            return {"action": "replace", "error": traceback.format_exc()}

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

        Args:
            tool_name: Nombre de la sub-herramienta (ej: 'files_list', 'files_read')
            payload: Payload con los argumentos
        """
        # Mapear nombres de herramientas a funciones
        name_to_func = {
            "files_list": "list",
            "files_search": "search",
            "files_read": "read",
            "files_write": "write",
            "files_replace": "replace"
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

        except Exception as e:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({"error": traceback.format_exc()})
            }

if __name__ == "__main__":
    # Ejemplo de uso de FilesBrowserTool

    # Crear la herramienta
    tool = FilesBrowserToolbox()

    # Simular la estructura de payload que vendría del modelo OpenAI
    class MockPayload:
        def __init__(self, arguments):
            self.function = MockFunction(arguments)


    class MockFunction:
        def __init__(self, arguments):
            self.arguments = json.dumps(arguments)


    print("=== Ejemplo 1: Listar archivos del directorio actual ===")
    payload1 = MockPayload({"path": ".", "show_hidden": False})
    response1 = tool.call("files_list", payload1)
    result1 = json.loads(response1['content'])
    print(f"Encontrados {result1.get('count', 0)} elementos en {result1.get('path', '')}")
    for item in result1.get('items', [])[:5]:  # Mostrar solo los primeros 5
        print(f"  {item['type']}: {item['name']}")

    print("\n=== Ejemplo 2: Buscar archivos Python ===")
    payload2 = MockPayload({"pattern": "*.py", "path": "."})
    response2 = tool.call("files_search", payload2)
    result2 = json.loads(response2['content'])
    print(f"Encontrados {result2.get('count', 0)} archivos Python")
    for match in result2.get('matches', [])[:3]:  # Mostrar solo los primeros 3
        print(f"  {match['name']} ({match.get('size', 0)} bytes)")

    print("\n=== Ejemplo 3: Crear y escribir archivo de prueba ===")
    test_content = """# Archivo de prueba
print("Hola mundo!")
x = 42
print(f"El valor es {x}")
"""
    payload3 = MockPayload({"file_path": "test_file.py", "content": test_content})
    response3 = tool.call("files_write", payload3)
    result3 = json.loads(response3['content'])
    if not result3.get('error'):
        print(f"Archivo creado: {result3.get('file_path')}")
        print(f"Bytes escritos: {result3.get('bytes_written')}")
        print(f"Líneas: {result3.get('lines_written')}")
    else:
        print(f"Error: {result3['error']}")

    print("\n=== Ejemplo 4: Leer archivo creado ===")
    payload4 = MockPayload({"file_path": "test_file.py"})
    response4 = tool.call("files_read", payload4)
    result4 = json.loads(response4['content'])
    if not result4.get('error'):
        print(f"Contenido leído ({result4.get('lines')} líneas):")
        print(result4.get('content', '')[:100] + "...")
    else:
        print(f"Error: {result4['error']}")

    print("\n=== Ejemplo 5: Reemplazar línea en archivo ===")
    payload5 = MockPayload({
        "file_path": "test_file.py",
        "old_line": "x = 42",
        "new_line": "x = 100  # Valor actualizado"
    })
    response5 = tool.call("files_replace", payload5)
    result5 = json.loads(response5['content'])
    if not result5.get('error'):
        print(f"Reemplazos realizados: {result5.get('replacements_made')}")
        print(f"Línea antigua: '{result5.get('old_line')}'")
        print(f"Línea nueva: '{result5.get('new_line')}'")
    else:
        print(f"Error: {result5['error']}")

    print("\n=== Configuración de herramientas para OpenAI ===")
    tools_config = tool.initialize()
    print(f"Se registraron {len(tools_config)} herramientas:")
    for config in tools_config:
        print(f"  - {config['function']['name']}: {config['function']['description']}")

    # Limpiar archivo de prueba
    try:
        os.remove("test_file.py")
        print("\n✓ Archivo de prueba eliminado")
    except:
        pass