import json
import os
import glob
import traceback
from pathlib import Path

class FilesBrowserToolbox:
    """
    Herramienta para navegación y manipulación de archivos para un agente OpenAI.

    Esta clase integra múltiples sub-herramientas relacionadas con archivos:
    - explore_directory: Explorar archivos y carpetas con filtros avanzados
    - search: Buscar archivos por patrón
    - read: Leer contenido de archivos
    - write: Escribir archivos completos
    - replace: Editar archivos mediante reemplazo de líneas
    - delete: Eliminar archivos o directorios

    Cada sub-herramienta tiene su propio conjunto de argumentos específicos,
    evitando conflictos entre parámetros excluyentes.
    """

    def __init__(self):
        self.toolbox_name = 'files_browser_toolbox'
        # Configuración de sub-herramientas disponibles
        self.sub_tools = {
            "explore_directory": self._explore_directory,
            "search": self._search_files,
            "read": self._read_file,
            "write": self._write_file,
            "replace": self._replace_in_file,
            "delete": self._delete_file_or_dir
        }

        # Configuración base para cada sub-herramienta
        self.tools_config = {
            "explore_directory": {
                "name": "files_explore_directory",
                "description": "Explora archivos y carpetas recursivamente con filtros avanzados",
                "arguments": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del directorio a explorar",
                        "default": "."
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Patrón de archivos a buscar",
                        "default": "*"
                    },
                    "dirs_excluidos": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de directorios a excluir",
                        "default": [".venv", "__pycache__", ".git", "build", "dist"]
                    },
                    "exts_excluidas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de extensiones a excluir (con punto)",
                        "default": [".jpg", ".jpeg", ".png", ".gif", ".pkl"]
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Búsqueda recursiva en subdirectorios",
                        "default": True
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
            },
            "delete": {
                "name": "files_delete",
                "description": "Elimina un archivo o directorio",
                "arguments": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del archivo o directorio a eliminar"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Para directorios: eliminar recursivamente todo el contenido",
                        "default": False
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Forzar eliminación sin confirmación adicional",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        }

    def _buscar_archivos(self, ruta_raiz, patron="*", *, dirs_excluidos=None, exts_excluidas=None):
        """
        Generador que busca archivos recursivamente, excluyendo de forma eficiente
        los directorios y extensiones especificados.
        """
        dirs_excluidos = dirs_excluidos or set()
        exts_excluidas = exts_excluidas or set()

        for raiz, dirs, archivos in os.walk(ruta_raiz):
            # Poda el árbol de búsqueda para no entrar en directorios excluidos
            dirs[:] = [d for d in dirs if d not in dirs_excluidos]

            for nombre_archivo in archivos:
                p = Path(raiz) / nombre_archivo
                if p.suffix not in exts_excluidas and p.match(patron):
                    yield str(p)

    def _explore_directory(self, path=".", pattern="*", dirs_excluidos=None, exts_excluidas=None, recursive=True, show_hidden=False):
        """Explora archivos y carpetas con filtros avanzados."""
        try:
            path = Path(path)
            if not path.exists():
                return {"error": f"La ruta '{path}' no existe"}

            if not path.is_dir():
                return {"error": f"La ruta '{path}' no es un directorio"}

            # Configurar valores por defecto
            if dirs_excluidos is None:
                dirs_excluidos = [".venv", "__pycache__", ".git", "build", "dist"]
            if exts_excluidas is None:
                exts_excluidas = [".jpg", ".jpeg", ".png", ".gif", ".pkl"]

            dirs_excluidos_set = set(dirs_excluidos)
            exts_excluidas_set = set(exts_excluidas)

            items = []

            if recursive:
                # Usar el método de búsqueda recursiva eficiente
                archivos_encontrados = list(self._buscar_archivos(
                    str(path),
                    pattern,
                    dirs_excluidos=dirs_excluidos_set,
                    exts_excluidas=exts_excluidas_set
                ))

                for archivo_path in archivos_encontrados:
                    archivo = Path(archivo_path)
                    if not show_hidden and archivo.name.startswith('.'):
                        continue

                    # Calcular ruta relativa de forma segura
                    try:
                        relative_path = str(archivo.relative_to(path.absolute()))
                    except ValueError:
                        # Si no se puede calcular la ruta relativa, usar la absoluta
                        relative_path = str(archivo.absolute())

                    items.append({
                        "name": archivo.name,
                        "type": "file",
                        "size": archivo.stat().st_size,
                        "path": str(archivo.absolute()),
                        "relative_path": relative_path
                    })

                # También incluir directorios encontrados durante el walk
                directorios_encontrados = set()
                for raiz, dirs, _ in os.walk(str(path)):
                    # Poda el árbol de búsqueda
                    dirs[:] = [d for d in dirs if d not in dirs_excluidos_set]

                    for dir_name in dirs:
                        dir_path = Path(raiz) / dir_name
                        if not show_hidden and dir_name.startswith('.'):
                            continue
                        directorios_encontrados.add(str(dir_path.absolute()))

                for dir_path_str in directorios_encontrados:
                    dir_path = Path(dir_path_str)

                    # Calcular ruta relativa de forma segura
                    try:
                        relative_path = str(dir_path.relative_to(path.absolute()))
                    except ValueError:
                        # Si no se puede calcular la ruta relativa, usar la absoluta
                        relative_path = str(dir_path.absolute())

                    items.append({
                        "name": dir_path.name,
                        "type": "directory",
                        "size": None,
                        "path": str(dir_path.absolute()),
                        "relative_path": relative_path
                    })

            else:
                # Exploración no recursiva (solo nivel actual)
                for item in path.iterdir():
                    if not show_hidden and item.name.startswith('.'):
                        continue

                    if item.is_dir() and item.name in dirs_excluidos_set:
                        continue

                    if item.is_file():
                        if item.suffix in exts_excluidas_set:
                            continue
                        if not item.match(pattern):
                            continue

                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None,
                        "path": str(item.absolute()),
                        "relative_path": item.name
                    })

            # Ordenar: directorios primero, luego archivos
            items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))

            return {
                "action": "explore_directory",
                "path": str(path.absolute()),
                "pattern": pattern,
                "recursive": recursive,
                "dirs_excluidos": dirs_excluidos,
                "exts_excluidas": exts_excluidas,
                "items": items,
                "count": len(items),
                "files_count": len([x for x in items if x["type"] == "file"]),
                "dirs_count": len([x for x in items if x["type"] == "directory"]),
                "error": ""
            }

        except Exception as e:
            return {"action": "explore_directory", "error": traceback.format_exc()}

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

    def _delete_file_or_dir(self, path, recursive=False, force=False):
        """Elimina un archivo o directorio."""
        try:
            target_path = Path(path)

            if not target_path.exists():
                return {"error": f"La ruta '{path}' no existe"}

            # Información sobre lo que se va a eliminar
            is_file = target_path.is_file()
            is_dir = target_path.is_dir()
            size = 0
            file_count = 0
            dir_count = 0

            if is_file:
                size = target_path.stat().st_size
                file_count = 1
            elif is_dir:
                # Contar archivos y directorios recursivamente
                for root, dirs, files in os.walk(target_path):
                    file_count += len(files)
                    dir_count += len(dirs)
                    for file in files:
                        try:
                            size += Path(root, file).stat().st_size
                        except:
                            pass  # Ignorar archivos que no se pueden leer
                dir_count += 1  # Incluir el directorio raíz

            # Validaciones de seguridad
            if is_dir and not recursive and any(target_path.iterdir()):
                return {
                    "error": f"El directorio '{path}' no está vacío. Use recursive=True para eliminarlo con su contenido"}

            # Realizar la eliminación
            if is_file:
                target_path.unlink()
                action_performed = "file_deleted"
            elif is_dir:
                if recursive:
                    import shutil
                    shutil.rmtree(target_path)
                    action_performed = "directory_deleted_recursive"
                else:
                    target_path.rmdir()  # Solo funciona si está vacío
                    action_performed = "empty_directory_deleted"

            return {
                "action": "delete",
                "action_performed": action_performed,
                "path": str(target_path.absolute()),
                "was_file": is_file,
                "was_directory": is_dir,
                "files_deleted": file_count,
                "directories_deleted": dir_count,
                "total_size_deleted": size,
                "recursive": recursive,
                "force": force,
                "error": ""
            }

        except PermissionError:
            return {"action": "delete", "error": f"Sin permisos para eliminar '{path}'"}
        except OSError as e:
            return {"action": "delete", "error": f"Error del sistema al eliminar '{path}': {str(e)}"}
        except Exception as e:
            return {"action": "delete", "error": traceback.format_exc()}

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

    def call(self, tool_name, payload, memory):
        """
        Ejecuta la sub-herramienta específica con los argumentos proporcionados.

        Args:
            tool_name: Nombre de la sub-herramienta (ej: 'files_explore_directory', 'files_read')
            payload: Payload con los argumentos
        """
        # Mapear nombres de herramientas a funciones
        name_to_func = {
            "files_explore_directory": "explore_directory",
            "files_search": "search",
            "files_read": "read",
            "files_write": "write",
            "files_replace": "replace",
            "files_delete": "delete"
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
            }, memory

        except Exception as e:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({"error": traceback.format_exc()})
            }, memory

if __name__ == "__main__":
    # Ejemplo de uso de FilesBrowserTool

    # Crear la herramienta
    tool = FilesBrowserToolbox()

    print("=== Ejemplo 1: Explorar directorio actual con filtros ===")
    payload1 = {
        "path": ".",
        "pattern": "*.py",
        "recursive": True,
        "dirs_excluidos": [".venv", "__pycache__", ".git"],
        "exts_excluidas": [".pyc", ".pkl"]
    }
    response1 = tool.call("files_explore_directory", payload1)
    result1 = json.loads(response1['content'])
    print(
        f"Encontrados {result1.get('count', 0)} elementos ({result1.get('files_count', 0)} archivos, {result1.get('dirs_count', 0)} directorios)")
    for item in result1.get('items', [])[:5]:  # Mostrar solo los primeros 5
        print(f"  {item['type']}: {item['relative_path']} ({item.get('size', 'N/A')} bytes)")

    print("\n=== Ejemplo 2: Buscar archivos Python ===")
    payload2 = {"pattern": "*.py", "path": "."}
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
    payload3 = {"file_path": "test_file.py", "content": test_content}
    response3 = tool.call("files_write", payload3)
    result3 = json.loads(response3['content'])
    if not result3.get('error'):
        print(f"Archivo creado: {result3.get('file_path')}")
        print(f"Bytes escritos: {result3.get('bytes_written')}")
        print(f"Líneas: {result3.get('lines_written')}")
    else:
        print(f"Error: {result3['error']}")

    print("\n=== Ejemplo 4: Leer archivo creado ===")
    payload4 = {"file_path": "test_file.py"}
    response4 = tool.call("files_read", payload4)
    result4 = json.loads(response4['content'])
    if not result4.get('error'):
        print(f"Contenido leído ({result4.get('lines')} líneas):")
        print(result4.get('content', '')[:100] + "...")
    else:
        print(f"Error: {result4['error']}")

    print("\n=== Ejemplo 5: Reemplazar línea en archivo ===")
    payload5 = {
        "file_path": "test_file.py",
        "old_line": "x = 42",
        "new_line": "x = 100  # Valor actualizado"
    }
    response5 = tool.call("files_replace", payload5)
    result5 = json.loads(response5['content'])
    if not result5.get('error'):
        print(f"Reemplazos realizados: {result5.get('replacements_made')}")
        print(f"Línea antigua: '{result5.get('old_line')}'")
        print(f"Línea nueva: '{result5.get('new_line')}'")
    else:
        print(f"Error: {result5['error']}")

    print("\n=== Ejemplo 6: Eliminar archivo de prueba ===")
    payload6 = {
        "path": "test_file.py",
        "force": True
    }
    response6 = tool.call("files_delete", payload6)
    result6 = json.loads(response6['content'])
    if not result6.get('error'):
        print(f"Eliminación exitosa: {result6.get('action_performed')}")
        print(f"Archivos eliminados: {result6.get('files_deleted')}")
        print(f"Tamaño total eliminado: {result6.get('total_size_deleted')} bytes")
    else:
        print(f"Error: {result6['error']}")

    print("\n=== Configuración de herramientas para OpenAI ===")
    tools_config = tool.initialize()
    print(f"Se registraron {len(tools_config)} herramientas:")
    for config in tools_config:
        print(f"  - {config['function']['name']}: {config['function']['description']}")