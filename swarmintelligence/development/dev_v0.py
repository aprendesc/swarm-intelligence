from eigenlib.utils.project_setup import ProjectSetupClass
ProjectSetupClass(project_folder='swarm-intelligence')


class AddNumbersTool:
    """
    Ejemplo básico de tool:
    – name            : nombre con el que el agente la invoca.
    – description     : texto corto para el modelo.
    – args            : metadatos de los parámetros (nombre, tipo, descripción, required).
    – get_tool_dict() : devuelve la especificación JSON-schema para la API “functions”.
    – run()           : lógica simple (a + b).
    """

    def __init__(self):
        self.name = "add_numbers"
        self.description = "Adds two numbers and returns the result."
        self.args = [
            {
                "name": "a",
                "type": "number",
                "description": "First summand.",
                "required": True
            },
            {
                "name": "b",
                "type": "number",
                "description": "Second summand.",
                "required": True
            }
        ]

    # Hook opcional para inicializar recursos (BD, modelos, etc.)
    def initialize(self):
        pass

    def get_tool_dict(self):
        """Devuelve la definición compatible con function-calling."""
        return self._gen_tool_dict(self.name, self.description, self.args)

    def run(self, a, b):
        """Suma dos números y devuelve la respuesta final que verá el agente."""
        return {"result": a + b}

    # ------------- helpers internos -------------
    def _gen_tool_dict(self, tool_name, tool_description, tool_args):
        """
        Construye el JSON-schema exigido por las APIs de function-calling
        (chat-completion, agente de LangChain, etc.).
        """
        args_schema = {}
        required = []
        for arg in tool_args:
            args_schema[arg["name"]] = {
                "type": arg["type"],
                "description": arg["description"]
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
                    "required": required
                }
            }
        }
from eigenlib.LLM.intelligent_web_search import IntelligentWebSearch
result = IntelligentWebSearch().run('Como se hace una tortilla', num_results=3)

from swarmintelligence.main import MainClass
from swarmintelligence.config import gp_assistant_config as config
main = MainClass(config)

main.initialize(config)
config['user_message'] = 'Busca el tiempo en Alpedrete'
updated_config = main.predict(config)
print(updated_config['state_dict']['answer'])