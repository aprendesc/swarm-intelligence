import json
import traceback
from ddgs import DDGS
from eigenlib.utils.parallel_io import ParallelIO
from eigenlib.LLM.sources_parser import SourcesParserClass

class WebSearchToolbox:
    """
    Herramienta para búsqueda web y extracción de contenido de URLs para un agente OpenAI.

    Esta clase integra múltiples sub-herramientas relacionadas con búsqueda web:
    - search: Búsqueda en DuckDuckGo para obtener URLs de resultados
    - extract: Extracción de contenido de URLs específicas en formato markdown

    Cada sub-herramienta tiene su propio conjunto de argumentos específicos,
    evitando conflictos entre parámetros excluyentes.
    """

    def __init__(self, default_max_results=5, default_region="wt-wt"):
        self.toolbox_name = 'web_search_toolbox'
        # Configuración por defecto
        self.default_max_results = default_max_results
        self.default_region = default_region

        # Configuración de sub-herramientas disponibles
        self.sub_tools = {
            "search": self._search_web,
            "extract": self._extract_urls
        }

        # Configuración base para cada sub-herramienta
        self.tools_config = {
            "search": {
                "name": "web_search",
                "description": "Obtiene las URL que coinciden con los resultados de busqueda de la query proporcionada.",
                "arguments": {
                    "query": {
                        "type": "string",
                        "description": "Consulta de búsqueda para obtener las URL."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Número máximo de resultados de búsqueda",
                        "default": 5
                    },
                    # "region": {
                    #     "type": "string",
                    #     "description": "Región para la búsqueda (ej: 'wt-wt', 'us-en', 'es-es')",
                    #     "default": "wt-wt"
                    # }
                },
                "required": ["query"]
            },
            "extract": {
                "name": "web_extract",
                "description": "Extrae y convierte a markdown el contenido de URLs proporcionadas u obtenidas a través de la herramienta search.",
                "arguments": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de URLs para extraer contenido"
                    }
                },
                "required": ["urls"]
            }
        }

    def _search_web(self, query, max_results=None, region=None):
        """Realiza búsqueda web usando DuckDuckGo."""
        try:
            # Usar valores por defecto si no se proporcionan
            max_results = max_results or self.default_max_results
            region = region or self.default_region

            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=max_results, region='wt-wt')
                results = list(results)  # Convertir generador a lista

            return {
                "action": "search",
                "query": query,
                "region": region,
                "results": results,
                "count": len(results),
                "error": ""
            }

        except Exception as e:
            return {
                "action": "search",
                "query": query,
                "results": [],
                "count": 0,
                "error": traceback.format_exc()
            }

    def _extract_urls(self, urls):
        """Extrae contenido de URLs en formato markdown usando procesamiento paralelo."""
        try:
            # Convertir string a lista si es necesario
            if isinstance(urls, str):
                urls = [urls]

            # Validar que todas las URLs sean strings
            if not all(isinstance(url, str) for url in urls):
                return {"error": "Todas las URLs deben ser strings"}

            # Configurar el parser y ejecutar en paralelo
            sp = SourcesParserClass()
            result = ParallelIO().run_in_parallel(
                sp.run,
                {},
                {'file_path': urls},
                max_workers=min(len(urls), 10),  # Limitar workers para evitar sobrecarga
                use_processes=False
            )

            return {
                "action": "extract",
                "urls": urls,
                "summary": '\n'.join(result) if result else "",
                "count": len(result) if result else 0,
                "success_count": len([r for r in result if r]) if result else 0,
                "error": ""
            }

        except Exception as e:
            return {
                "action": "extract",
                "urls": urls if isinstance(urls, list) else [urls],
                "summary": "",
                "count": 0,
                "success_count": 0,
                "error": traceback.format_exc()
            }

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
            tool_name: Nombre de la sub-herramienta ('web_search', 'web_extract')
            payload: Payload con los argumentos
        """
        # Mapear nombres de herramientas a funciones
        name_to_func = {
            "web_search": "search",
            "web_extract": "extract"
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
    # Ejemplo de uso de WebSearchTool con filosofía multi-herramienta

    # Crear la herramienta
    tool = WebSearchToolbox()


    print("=== Ejemplo 1: Búsqueda web con web_search ===")
    payload1 = {
        "query": "inteligencia artificial 2024",
        "max_results": 3,
        "region": "es-es"
    }
    response1 = tool.call("web_search", payload1)
    result1 = json.loads(response1['content'])
    print(f"Búsqueda encontró {result1.get('count', 0)} resultados")
    if result1.get('results'):
        for i, r in enumerate(result1['results'][:2], 1):
            print(f"  {i}. {r.get('title', 'Sin título')}")
            print(f"     URL: {r.get('href', 'Sin URL')}")

    print("\n=== Ejemplo 2: Extracción con web_extract ===")
    payload2 = {
        "urls": ["https://example.com", "https://httpbin.org/html"]
    }
    response2 = tool.call("web_extract", payload2)
    result2 = json.loads(response2['content'])
    print(f"Extracción de {len(result2.get('urls', []))} URL(s)")
    print(f"Extracciones exitosas: {result2.get('success_count', 0)}")
    if result2.get('error'):
        print(f"Error: {result2['error'][:100]}...")
    else:
        summary_preview = result2.get('summary', '')[:200]
        print(f"Contenido (preview): {summary_preview}...")

    print("\n=== Ejemplo 3: Búsqueda con parámetros por defecto ===")
    payload3 = {
        "query": "Python programming"
    }
    response3 = tool.call("web_search", payload3)
    result3 = json.loads(response3['content'])
    print(f"Búsqueda con defaults: {result3.get('count', 0)} resultados")
    print(f"Región utilizada: {result3.get('region', 'N/A')}")

    print("\n=== Ejemplo 4: Error en búsqueda (query vacía) ===")
    payload4 = {}
    response4 = tool.call("web_search", payload4)
    result4 = json.loads(response4['content'])
    if result4.get('error'):
        print(f"Error esperado capturado correctamente")

    print("\n=== Ejemplo 5: Extracción de URL única (string) ===")
    payload5 = {
        "urls": ["https://httpbin.org/json"]
    }
    response5 = tool.call("web_extract", payload5)
    result5 = json.loads(response5['content'])
    print(f"Extracción de URL única: {result5.get('count', 0)} resultados")

    print("\n=== Configuración de herramientas para OpenAI ===")
    tools_config = tool.initialize()
    print(f"Se registraron {len(tools_config)} herramientas:")
    for config in tools_config:
        print(f"  - {config['function']['name']}: {config['function']['description']}")
        required = config['function']['parameters'].get('required', [])
        print(f"    Parámetros requeridos: {required}")