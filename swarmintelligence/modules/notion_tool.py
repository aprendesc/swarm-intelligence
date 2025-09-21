import json
from typing import Any, Dict, List, Optional
from eigenlib.utils.notion_io import NotionIO
import types

ALLOWED_PROJECTS = ['jedi', 'test_project']
ALLOWED_STATUS = ['Active', 'Fixed', 'Stand By']


class NotionTool:
    """
    Tool que expone operaciones básicas de Notion como función invocable
    dentro de un agente OpenAI, siguiendo la interfaz del framework.

    Operaciones implementadas:
    - get_database_pages
    - create_database_page (usa los argumentos fijos: name, project, status, target_date, content)
    - read_page_as_markdown
    - update_page_properties (usa los argumentos fijos: name, project, status, target_date)
    - delete_page
    - write_page_content (reemplaza write_text, con soporte para Markdown y clear_existing)
    """

    def __init__(self, auth_token: str, database_id="2262a599-e985-8017-9faf-dd11b3b8df8b"):
        self.tool_name = "notion_tool"
        self.tool_description = "Gestiona bases de datos y páginas en Notion (leer, crear, actualizar, borrar, escribir contenido Markdown)."
        self.notion = NotionIO(auth_token=auth_token)
        # ID por defecto de la database (la usaré automáticamente)
        self.database_id = database_id

        # Definición del esquema de argumentos (para initialize)
        self.arguments = {
            "operation": {
                "type": "string",
                "description": "La operación a realizar en Notion",
                "enum": [
                    "get_database_pages",
                    "create_database_page",
                    "read_page_as_markdown",
                    "update_page_properties",
                    "delete_page",
                    "write_page_content"
                ]
            },
            # Identificadores (cuando apliquen)
            "page_id": {
                "type": "string",
                "description": "ID de la página (requerido para read/update/delete/write_page_content)."
            },
            # Argumentos fijos para create/update (requeridos según operación)
            "name": {
                "type": "string",
                "description": "Título (Name) de la página."
            },
            "project": {
                "type": "array",
                "items": {"type": "string", "enum": ALLOWED_PROJECTS},
                "description": f"Lista de proyectos. enum={ALLOWED_PROJECTS}"
            },
            "status": {
                "type": "string",
                "enum": ALLOWED_STATUS,
                "description": f"Estado de la página. enum={ALLOWED_STATUS}"
            },
            "target_date": {
                "type": "string",
                "description": "Fecha como string (YYYY-MM-DD). Obligatorio para crear paginas. La fecha de hoy es el valor por defecto."
            },
            "content": {
                "type": "string",
                "description": "Contenido Markdown a escribir en la página. Soporta encabezados, listas, código, citas, etc."
            },
            "clear_existing": {
                "type": "boolean",
                "description": "Para write_page_content: si True, limpia el contenido existente antes de escribir. Default: false",
                "default": False
            }
        }

        # Solo operation es estrictamente requerido en el schema general.
        # (Las demás son requeridas condicionalmente según la operación.)
        self.required = ["operation"]

    # ---------- Helpers ----------
    def _build_properties_from_fixed_args(
            self,
            name: Optional[str],
            project: Optional[List[str]],
            status: Optional[str],
            target_date: Optional[str]
    ) -> Dict[str, Any]:
        """
        Construye el dict 'properties' esperado por NotionIO a partir de los
        argumentos fijos 'name', 'project', 'status', 'target_date'.
        Filtra/normaliza projects y status contra los enums permitidos.
        """
        props: Dict[str, Any] = {}
        if name:
            props["Name"] = name

        if project:
            # Normalizar y filtrar proyectos inválidos
            valid = [p for p in project if p in ALLOWED_PROJECTS]
            if not valid and project:
                # Si el usuario pasó proyectos pero ninguno válido, registrar y usar el original
                self.notion.logger.warning(f"Project items inválidos: {project}. Se ignorarán los inválidos.")
            if valid:
                props["Project"] = valid

        if status:
            if status not in ALLOWED_STATUS:
                self.notion.logger.warning(f"Status inválido: {status}. Valores permitidos: {ALLOWED_STATUS}")
            else:
                props["Status"] = status

        if target_date:
            # No hacemos parsing estricto; NotionIO admite strings tipo 'YYYY-MM-DD'
            props["Target Date"] = target_date

        return props

    # ---------- Núcleo funcional ----------
    def _method(self, operation: str, **kwargs) -> Any:
        """
        Ejecuta la operación sobre Notion. kwargs proviene del JSON decodificado.
        """
        # Asegurar database_id disponible
        database_id = kwargs.get("database_id", self.database_id)

        if operation == "get_database_pages":
            try:
                pages = self.notion.get_database_pages(database_id=database_id)
                # NotionIO retorna un DataFrame en tu implementación; convertir a lista de records si es DataFrame
                try:
                    return pages.to_dict(orient="records")
                except Exception:
                    return pages  # si ya es lista, devolver tal cual
            except Exception as e:
                self.notion.logger.error(f"Error en get_database_pages: {e}")
                return {"error": str(e)}

        elif operation == "create_database_page":
            name = kwargs.get("name")
            project = kwargs.get("project")
            status = kwargs.get("status")
            target_date = kwargs.get("target_date")
            content = kwargs.get("content")

            # Validación mínima: name y project y status y target_date deberían suministrarse
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
                return {"error": f"Faltan argumentos obligatorios para create_database_page: {missing}"}

            properties = self._build_properties_from_fixed_args(name, project, status, target_date)
            try:
                page_id = self.notion.create_database_page(database_id=database_id, properties=properties,
                                                           content=content)
                return {"page_id": page_id}
            except Exception as e:
                self.notion.logger.error(f"Error creando página: {e}")
                return {"error": str(e)}

        elif operation == "read_page_as_markdown":
            page_id = kwargs.get("page_id")
            if not page_id:
                return {"error": "page_id requerido para read_page_as_markdown"}
            try:
                md = self.notion.read_page_as_markdown(page_id=page_id)
                return {"markdown": md}
            except Exception as e:
                self.notion.logger.error(f"Error leyendo página: {e}")
                return {"error": str(e)}

        elif operation == "update_page_properties":
            page_id = kwargs.get("page_id")
            if not page_id:
                return {"error": "page_id requerido para update_page_properties"}

            name = kwargs.get("name")
            project = kwargs.get("project")
            status = kwargs.get("status")
            target_date = kwargs.get("target_date")

            # Si no se provee ningún argumento para actualizar, devolver error
            if not any([name, project, status, target_date]):
                return {"error": "Se requiere al menos uno de: name, project, status, target_date para actualizar"}

            properties = self._build_properties_from_fixed_args(name, project, status, target_date)
            try:
                ok = self.notion.update_page_properties(page_id=page_id, properties=properties)
                return {"ok": ok}
            except Exception as e:
                self.notion.logger.error(f"Error actualizando propiedades: {e}")
                return {"error": str(e)}

        elif operation == "delete_page":
            page_id = kwargs.get("page_id")
            if not page_id:
                return {"error": "page_id requerido para delete_page"}
            try:
                ok = self.notion.delete_page(page_id=page_id)
                return {"ok": ok}
            except Exception as e:
                self.notion.logger.error(f"Error borrando (archivando) página: {e}")
                return {"error": str(e)}

        elif operation == "write_page_content":
            page_id = kwargs.get("page_id")
            content = kwargs.get("content", "")
            clear_existing = kwargs.get("clear_existing", False)

            if not page_id:
                return {"error": "page_id requerido para write_page_content"}

            if not content:
                return {"error": "content requerido para write_page_content"}

            try:
                # Usar el método write_page_content de NotionIO que soporta Markdown y clear_existing
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
                self.notion.logger.error(f"Error escribiendo contenido Markdown: {e}")
                return {"error": str(e)}

        else:
            return {"error": f"Operación no soportada: {operation}"}

    # ---------- Interfaz para OpenAI ----------
    def initialize(self) -> Dict[str, Any]:
        """
        Devuelve la definición de la tool en formato JSON Schema para OpenAI.
        """
        cfg = {
            "type": "function",
            "function": {
                "name": self.tool_name,
                "description": self.tool_description,
                "parameters": {
                    "type": "object",
                    "properties": self.arguments,
                    "required": self.required
                }
            }
        }
        return cfg

    def call(self, payload):
        """
        Ejecuta la operación en Notion usando los argumentos enviados por el modelo.

        `payload` es el objeto simulado que contiene `function.arguments` (JSON string).
        """
        # Si recibimos un SimpleNamespace como en tus ejemplos de test, extraer arguments
        if hasattr(payload, "function") and hasattr(payload.function, "arguments"):
            args = json.loads(payload.function.arguments)
        elif isinstance(payload, dict):
            args = payload.copy()
        else:
            raise ValueError("payload inesperado. Se esperaba objeto con payload.function.arguments o dict.")

        # Inyectar database_id por defecto si no viene
        args.setdefault("database_id", self.database_id)

        result = self._method(**args)
        return json.dumps({
            "role": "tool",
            "name": self.tool_name,
            "content": json.dumps({"result": result}, ensure_ascii=False)
        })


# ===========================
# Ejemplos de uso (para probar)
# ===========================
if __name__ == "__main__":
    NOTION_TOKEN = "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"
    tool = NotionTool(auth_token=NOTION_TOKEN)


    def make_payload(arguments: dict):
        return types.SimpleNamespace(
            function=types.SimpleNamespace(
                arguments=json.dumps(arguments, ensure_ascii=False)
            )
        )


    print("\n=== Inicialización de la tool ===")
    print(json.dumps(tool.initialize(), indent=2, ensure_ascii=False))

    # 1) Leer database
    payload = make_payload({
        "operation": "get_database_pages"
    })
    print("\n=== Leer database ===")
    print(tool.call(payload))

    # 2) Crear página con contenido Markdown complejo
    payload = make_payload({
        "operation": "create_database_page",
        "name": "Página con Markdown Avanzado",
        "project": ["jedi"],
        "status": "Active",
        "target_date": "2025-01-01",
        "content": """# Documento de Prueba

Este es un documento creado con **NotionTool mejorado** que soporta contenido Markdown completo.

## Características implementadas
- ✅ Soporte completo para Markdown
- ✅ Mecánica de reemplazo de contenido
- ✅ Preservación del formato original
- ✅ Manejo robusto de errores

### Ejemplo de código
```python
def test_notion_tool():
    tool = NotionTool(auth_token="your_token")
    result = tool.write_page_content(page_id, content, clear_existing=True)
    return result
```

> Este contenido fue generado automáticamente usando la versión mejorada de NotionTool.

### Lista de tareas
- [x] Implementar write_page_content
- [x] Añadir soporte para clear_existing
- [ ] Documentar los cambios
- [ ] Crear tests unitarios

---

**Nota final**: La herramienta ahora utiliza `write_page_content` en lugar del método básico anterior."""
    })
    print("\n=== Crear página con Markdown avanzado ===")
    create_result = tool.call(payload)
    print(create_result)

    # Extraer page_id del resultado (simulando)
    try:
        result_data = json.loads(create_result)
        page_id = json.loads(result_data["content"])["result"]["page_id"]

        # 3) Añadir contenido adicional sin limpiar
        payload = make_payload({
            "operation": "write_page_content",
            "page_id": page_id,
            "content": """
## Contenido Adicional

Este contenido fue **añadido** a la página existente usando `clear_existing=False`.

### Nuevas funcionalidades
1. Contenido incremental
2. Preservación del contenido anterior
3. Soporte completo para todos los elementos Markdown

```javascript
console.log("Contenido añadido exitosamente!");
```
""",
            "clear_existing": False
        })
        print("\n=== Añadir contenido sin limpiar ===")
        print(tool.call(payload))

        # 4) Reemplazar todo el contenido
        payload = make_payload({
            "operation": "write_page_content",
            "page_id": page_id,
            "content": """# Página Completamente Nueva

Todo el contenido anterior ha sido **reemplazado** usando `clear_existing=True`.

## Características del reemplazo
- El contenido anterior fue eliminado
- Este es contenido completamente nuevo
- Demuestra la funcionalidad de reemplazo

### Código de demostración
```bash
# Comando para reemplazar contenido
notion_tool.write_page_content(page_id, new_content, clear_existing=True)
```

> **Importante**: Esta funcionalidad permite actualizaciones completas de páginas.

¡La mejora está funcionando perfectamente!
""",
            "clear_existing": True
        })
        print("\n=== Reemplazar contenido completamente ===")
        print(tool.call(payload))

        # 5) Leer contenido final como Markdown
        payload = make_payload({
            "operation": "read_page_as_markdown",
            "page_id": page_id
        })
        print("\n=== Leer contenido final ===")
        print(tool.call(payload))

        # 6) Limpiar: eliminar página de prueba
        payload = make_payload({
            "operation": "delete_page",
            "page_id": page_id
        })
        print("\n=== Eliminar página de prueba ===")
        print(tool.call(payload))

    except Exception as e:
        print(f"Error en el ejemplo: {e}")
        print("Nota: Reemplaza 'tu_page_id' con un page_id real para probar las operaciones de escritura.")

    # Ejemplo adicional: Uso directo con page_id conocido
    print("\n=== Ejemplo con page_id fijo ===")
    payload = make_payload({
        "operation": "write_page_content",
        "page_id": "tu_page_id_real",
        "content": "# Test\n\nEste es un test de la funcionalidad mejorada.",
        "clear_existing": False
    })
    print("Payload para write_page_content:")
    print(json.dumps(json.loads(payload.function.arguments), indent=2, ensure_ascii=False))