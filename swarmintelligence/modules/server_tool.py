import json
import os
from eigenlib.utils.network_io import NetworkIO

class ServerTool:
    """
    Tool adaptada para comunicarse con el MCP server.
    Interfaz compatible con function-calling:
      - initialize() -> devuelve cfg (esquema)
      - call(payload) -> ejecuta llamada al servidor con los argumentos recibidos
    Uso:
      payload.function.arguments debe ser un JSON string con:
        {
          "config": { ... }   # parámetros específicos para el método
        }
    """

    def __init__(self, method, default_config, tool_name, tool_description, tool_args, max_output_length=1000):
        self.method = method
        self.tool_name = tool_name
        self.tool_description = tool_description
        self.tool_args = tool_args
        self.default_config = default_config
        self.max_output_length = max_output_length

        # Configuración de servidor MCP
        self.server_config = {
            'master_address': "localhost:5001",
            'client_name': os.environ.get('PACKAGE_NAME', 'default') + '_client',
            'password': 'test_pass',
            'delay': 1,
            'target_node': 'swarmautomations_node',
            'payload': {},
        }

    def initialize(self):
        """Devuelve la especificación de la tool (schema para function-calling)."""
        args_schema = {}
        required = []
        for arg in self.tool_args:
            args_schema[arg["name"]] = {
                "type": arg["type"],
                "description": arg["description"],
            }
            if arg.get("required"):
                required.append(arg["name"])
            if "items" in arg:
                args_schema[arg["name"]]['items'] = arg['items']

        self.cfg = {
            "type": "function",
            "function": {
                "name": self.tool_name,
                "description": self.tool_description,
                "parameters": {
                    "type": "object",
                    "properties": args_schema,
                    "required": required,
                },
            },
        }
        return self.cfg

    def _parse_payload_args(self, payload):
        """Extrae y parsea los argumentos de payload.function.arguments"""
        args_json = "{}"
        try:
            args_json = payload["function"]["arguments"]
        except Exception:
            try:
                args_json = payload.function.arguments
            except Exception:
                pass

        try:
            args = json.loads(args_json)
        except Exception:
            args = args_json if isinstance(args_json, dict) else {}
        return args

    def _limit_output(self, text: str) -> str:
        """Recorta la salida si excede el límite definido."""
        if len(text) > self.max_output_length:
            return text[:self.max_output_length] + f'... [OUTPUT TRUNCATED: length>{self.max_output_length}]'
        return text

    def _call_MCP_server(self, config):
        """Lógica para llamar al servidor MCP."""
        MASTER_ADDRESS = config['master_address']
        client_name = config['client_name']
        delay = config['delay']
        password = config['password']
        target_node = config['target_node']
        payload = config['payload']

        client = NetworkIO()
        client.launch_node(node_name=client_name, master_address=MASTER_ADDRESS, node_method=lambda: "OK", delay=delay, password=password)
        resultado = client.call(target_node=target_node, payload=payload)
        client.stop()
        config['result'] = resultado
        return config

    def call(self, payload):
        """Ejecuta la llamada al MCP server con los argumentos recibidos en el payload."""
        config = payload | self.default_config

        try:
            server_config = self.server_config.copy()
            server_config['payload'] = {'method': self.method, 'config': config}
            results = self._call_MCP_server(server_config)['result']['result']
            response = {
                "role": "tool",
                "name": self.tool_name,
                "content": json.dumps({"result": results})
            }
            return self._limit_output(json.dumps(response))

        except Exception as e:
            err = {"error": str(e) + ' -> The tool server failed. Stop the execution and inform the user.'}
            response = {
                "role": "tool",
                "name": self.tool_name,
                "content": json.dumps(err)
            }
            return self._limit_output(json.dumps(response))


if __name__ == "__main__":
    # Ejemplo de uso
    tool = ServerTool(
        method="example_method",
        default_config={"param1": "default"},
        tool_name="mcp_server_tool",
        tool_description="Herramienta que envía payloads al MCP server.",
        tool_args=[{"name": "config", "type": "object", "description": "Configuración para la llamada", "required": True}]
    )

    cfg = tool.initialize()
    print("Configuración inicial:")
    print(json.dumps(cfg, indent=2, ensure_ascii=False))

    payload = {
        "function": {
            "arguments": json.dumps({
                "config": {"param1": "custom_value"}
            })
        }
    }

    print("\nEjecutando payload de prueba...")
    response = tool.call(payload)
    print("Respuesta:")
    print(response)
