import json
import types
from typing import Any, Dict, List, Optional
from eigenlib.utils.notion_io import NotionIO

ALLOWED_STATUS = ['Active', 'Fixed', 'Stand By']


class NotionToolbox:
    """
    Tool que expone operaciones básicas de Notion como sub-tools invocables.
    Sub-tools:
      - notion_get_database_pages
      - notion_create_database_page
      - notion_read_page_as_markdown
      - notion_update_page_properties
      - notion_delete_page
      - notion_write_page_content
    """
    def __init__(
        self,
        auth_token: str,
        database_id: str = "2262a599-e985-8017-9faf-dd11b3b8df8b",
        ALLOWED_PROJECTS: Optional[List[str]] = None
    ):
        if ALLOWED_PROJECTS is None:
            ALLOWED_PROJECTS = []

        self.ALLOWED_PROJECTS = ALLOWED_PROJECTS
        self.tool_base = "notion_tool"  # base name (no se usa directamente)
        self.tool_description = "Operaciones CRUD y de contenido Markdown sobre Notion."
        self.notion = NotionIO(auth_token=auth_token)
        self.database_id = database_id

        # Mapeo de funciones internas
        self.sub_tools = {
            "get_database_pages": self._get_database_pages,
            "create_database_page": self._create_database_page,
            "read_page_as_markdown": self._read_page_as_markdown,
            "update_page_properties": self._update_page_properties,
            "delete_page": self._delete_page,
            "write_page_content": self._write_page_content
        }

        # Configuración por sub-tool (para get_tools)
        self.tools_config = {
            "get_database_pages": {
                "name": "notion_get_database_pages",
                "description": "Devuelve páginas de la database de Notion (opcional: database_id).",
                "arguments": {
                    "database_id": {"type": "string", "description": "ID de la database (opcional)."}
                },
                "required": []
            },
            "create_database_page": {
                "name": "notion_create_database_page",
                "description": "Crea una nueva página en la database (name, project, status, target_date obligatorios).",
                "arguments": {
                    "name": {"type": "string", "description": "Título de la página."},
                    "project": {
                        "type": "array",
                        "items": {"type": "string", "enum": self.ALLOWED_PROJECTS},
                        "description": f"Lista de proyectos. enum={self.ALLOWED_PROJECTS}"
                    },
                    "status": {"type": "string", "enum": ALLOWED_STATUS, "description": f"enum={ALLOWED_STATUS}"},
                    "target_date": {"type": "string", "description": "Fecha YYYY-MM-DD"},
                    "content": {"type": "string", "description": "Contenido Markdown inicial (opcional)."},
                    "database_id": {"type": "string", "description": "ID de la database (opcional)."}
                },
                "required": ["name", "project", "status", "target_date"]
            },
            "read_page_as_markdown": {
                "name": "notion_read_page_as_markdown",
                "description": "Lee una página y devuelve su contenido en Markdown.",
                "arguments": {
                    "page_id": {"type": "string", "description": "ID de la página a leer."}
                },
                "required": ["page_id"]
            },
            "update_page_properties": {
                "name": "notion_update_page_properties",
                "description": "Actualiza properties de una página (al menos uno de name/project/status/target_date).",
                "arguments": {
                    "page_id": {"type": "string", "description": "ID de la página."},
                    "name": {"type": "string", "description": "Nuevo título (opcional)."},
                    "project": {
                        "type": "array",
                        "items": {"type": "string", "enum": self.ALLOWED_PROJECTS},
                        "description": f"Lista de proyectos. enum={self.ALLOWED_PROJECTS}"
                    },
                    "status": {"type": "string", "enum": ALLOWED_STATUS},
                    "target_date": {"type": "string", "description": "Fecha YYYY-MM-DD (opcional)."}
                },
                "required": ["page_id"]
            },
            "delete_page": {
                "name": "notion_delete_page",
                "description": "Archiva (elimina lógicamente) una página por page_id.",
                "arguments": {
                    "page_id": {"type": "string", "description": "ID de la página a borrar."}
                },
                "required": ["page_id"]
            },
            "write_page_content": {
                "name": "notion_write_page_content",
                "description": "Escribe contenido Markdown en una página. Puede limpiar el existente.",
                "arguments": {
                    "page_id": {"type": "string", "description": "ID de la página."},
                    "content": {"type": "string", "description": "Contenido Markdown a escribir."},
                    "clear_existing": {"type": "boolean", "description": "Si True, limpia contenido previo.", "default": False}
                },
                "required": ["page_id", "content"]
            }
        }

    # ---------- Helpers ----------
    def _build_properties_from_fixed_args(
        self,
        name: Optional[str],
        project: Optional[List[str]],
        status: Optional[str],
        target_date: Optional[str]
    ) -> Dict[str, Any]:
        props: Dict[str, Any] = {}
        if name:
            props["Name"] = name

        if project:
            valid = [p for p in project if p in self.ALLOWED_PROJECTS]
            if not valid and project:
                # registrar advertencia en el logger de NotionIO
                try:
                    self.notion.logger.warning(f"Project items inválidos: {project}. Se ignorarán los inválidos.")
                except Exception:
                    pass
            if valid:
                props["Project"] = valid

        if status:
            if status not in ALLOWED_STATUS:
                try:
                    self.notion.logger.warning(f"Status inválido: {status}. Valores permitidos: {ALLOWED_STATUS}")
                except Exception:
                    pass
            else:
                props["Status"] = status

        if target_date:
            props["Target Date"] = target_date

        return props

    # ---------- Sub-tools (implementaciones) ----------
    def _get_database_pages(self, database_id: Optional[str] = None) -> Any:
        db_id = database_id or self.database_id
        try:
            pages = self.notion.get_database_pages(database_id=db_id)
            try:
                return {"pages": pages.to_dict(orient="records")}
            except Exception:
                return {"pages": pages}
        except Exception as e:
            try:
                self.notion.logger.error(f"Error en get_database_pages: {e}")
            except Exception:
                pass
            return {"error": str(e)}

    def _create_database_page(
        self,
        name: str,
        project: List[str],
        status: str,
        target_date: str,
        content: Optional[str] = None,
        database_id: Optional[str] = None
    ) -> Any:
        db_id = database_id or self.database_id
        missing = []
        if not name:
            missing.append("name")
        if not project:
            missing.append("project")
        if not status:
            missing.append("status")
        if not target_date:
            missing.append("target_date")
        if missing:
            return {"error": f"Faltan argumentos obligatorios: {missing}"}

        properties = self._build_properties_from_fixed_args(name, project, status, target_date)
        try:
            page_id = self.notion.create_database_page(database_id=db_id, properties=properties, content=content)
            return {"page_id": page_id}
        except Exception as e:
            try:
                self.notion.logger.error(f"Error creando página: {e}")
            except Exception:
                pass
            return {"error": str(e)}

    def _read_page_as_markdown(self, page_id: str) -> Any:
        if not page_id:
            return {"error": "page_id requerido"}
        try:
            md = self.notion.read_page_as_markdown(page_id=page_id)
            return {"markdown": md}
        except Exception as e:
            try:
                self.notion.logger.error(f"Error leyendo página: {e}")
            except Exception:
                pass
            return {"error": str(e)}

    def _update_page_properties(
        self,
        page_id: str,
        name: Optional[str] = None,
        project: Optional[List[str]] = None,
        status: Optional[str] = None,
        target_date: Optional[str] = None
    ) -> Any:
        if not page_id:
            return {"error": "page_id requerido"}

        if not any([name, project, status, target_date]):
            return {"error": "Se requiere al menos uno de: name, project, status, target_date"}

        properties = self._build_properties_from_fixed_args(name, project, status, target_date)
        try:
            ok = self.notion.update_page_properties(page_id=page_id, properties=properties)
            return {"ok": ok}
        except Exception as e:
            try:
                self.notion.logger.error(f"Error actualizando propiedades: {e}")
            except Exception:
                pass
            return {"error": str(e)}

    def _delete_page(self, page_id: str) -> Any:
        if not page_id:
            return {"error": "page_id requerido"}
        try:
            ok = self.notion.delete_page(page_id=page_id)
            return {"ok": ok}
        except Exception as e:
            try:
                self.notion.logger.error(f"Error borrando página: {e}")
            except Exception:
                pass
            return {"error": str(e)}

    def _write_page_content(self, page_id: str, content: str, clear_existing: bool = False) -> Any:
        if not page_id:
            return {"error": "page_id requerido"}
        if not content:
            return {"error": "content requerido"}
        try:
            ok = self.notion.write_page_content(
                page_id=page_id,
                markdown_content=content,
                clear_existing=clear_existing
            )
            action = "reemplazado" if clear_existing else "añadido"
            return {
                "ok": ok,
                "message": f"Contenido Markdown {action} exitosamente en la página",
                "clear_existing": clear_existing,
                "content_length": len(content)
            }
        except Exception as e:
            try:
                self.notion.logger.error(f"Error escribiendo contenido Markdown: {e}")
            except Exception:
                pass
            return {"error": str(e)}

    # ---------- Interfaz para OpenAI (get_tools + call) ----------
    def initialize(self) -> List[Dict[str, Any]]:
        """
        Devuelve todas las sub-herramientas como funciones independientes (JSON Schema)
        en formato compatible con OpenAI function-calling.
        """
        tools = []
        for key, cfg in self.tools_config.items():
            tool_config = {
                "type": "function",
                "function": {
                    "name": cfg["name"],
                    "description": cfg["description"],
                    "parameters": {
                        "type": "object",
                        "properties": cfg["arguments"],
                        "required": cfg["required"]
                    }
                }
            }
            tools.append(tool_config)
        return tools

    def call(self, tool_name: str, payload: Any) -> Dict[str, Any]:
        """
        Ejecuta la sub-tool indicada por `tool_name`. `payload` puede ser:
         - un objeto con payload.function.arguments (como SimpleNamespace en tests)
         - un dict con los argumentos directamente
        Devuelve un dict con keys: role, name, content (content -> JSON string).
        """
        # Mapear nombres de función a las claves internas de sub_tools
        name_to_key = {cfg["name"]: key for key, cfg in self.tools_config.items()}
        func_key = name_to_key.get(tool_name)
        if not func_key:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({"error": f"Herramienta '{tool_name}' no encontrada"})
            }

        # Obtener args
        if hasattr(payload, "function") and hasattr(payload.function, "arguments"):
            args = json.loads(payload.function.arguments)
        elif isinstance(payload, dict):
            args = payload.copy()
        else:
            raise ValueError("payload inesperado. Se esperaba objeto con payload.function.arguments o dict.")

        # Inyectar database_id por defecto cuando aplique
        args.setdefault("database_id", self.database_id)

        try:
            result = self.sub_tools[func_key](**args)
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(result, ensure_ascii=False)
            }
        except TypeError as te:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({"error": f"Argumentos inválidos: {te}"})
            }
        except Exception as e:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({"error": str(e)})
            }


# ===========================
# Ejemplos de uso (prueba)
# ===========================
if __name__ == "__main__":
    # Usa una variable segura / placeholder en lugar de un token hardcodeado.
    NOTION_TOKEN = "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"
    tool = NotionToolbox(auth_token=NOTION_TOKEN, ALLOWED_PROJECTS=["jedi", "apollo", "infra"])

    def make_payload(arguments: dict):
        return types.SimpleNamespace(
            function=types.SimpleNamespace(
                arguments=json.dumps(arguments, ensure_ascii=False)
            )
        )

    # Mostrar herramientas a registrar
    print("Herramientas disponibles para registrar:")
    for t in tool.initialize():
        print(" -", t["function"]["name"])

    # Ejemplo: listar database pages
    payload = make_payload({"database_id": tool.database_id})
    print("\n-> Llamando a notion_get_database_pages")
    print(tool.call("notion_get_database_pages", payload))

    # Ejemplo: crear página (si tienes token válido)
    payload = make_payload({
        "name": "Página de prueba (API)",
        "project": ["jedi"],
        "status": "Active",
        "target_date": "2025-01-01",
        "content": "# Hola\nContenido de prueba"
    })
    print("\n-> Crear página (notion_create_database_page)")
    print(tool.call("notion_create_database_page", payload))
