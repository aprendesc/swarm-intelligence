import json
import traceback
from eigenlib.genai.memory import Memory

class AgentCommunicationToolbox:
    """
    Herramienta para consultar a un agente específico y obtener su respuesta.

    Esta herramienta sigue la filosofía del framework y permite encapsular
    la consulta a un agente como una herramienta que puede ser utilizada
    por otros agentes o sistemas.
    """

    def __init__(self, agent_instance, agent_name=None, description=None):
        """
        Inicializa la herramienta de consulta de agente.

        Args:
            agent_instance: Instancia del agente que se va a consultar
            agent_name: Nombre descriptivo del agente para logs y referencias
        """
        self.toolbox_name = 'agent_consultation_toolbox'
        self.agent_instance = agent_instance
        self.agent_name = agent_name

        # Sub-herramientas (en este caso solo una)
        self.sub_tools = {
            self.agent_name + "_tool": self._consult_agent
        }

        # Configuración de herramientas
        self.tools_config = {
            self.agent_name + "_tool": {
                "name": self.agent_name + "_tool",
                "description": description,
                "arguments": {
                    "query": {
                        "type": "string",
                        "description": "Pregunta o solicitud que se enviará al agente. Debe ser una consulta detallada con todo lujo de detalles."
                    },
                },
                "required": ["query"]
            }
        }

    def _consult_agent(self, memory, query):
        """
        Consulta al agente con una pregunta específica.

        Args:
            query (str): Pregunta o solicitud para el agente
            context (str): Contexto adicional opcional

        Returns:
            dict: Resultado de la consulta con la respuesta del agente
        """
        try:
            memory, agent_response = self.agent_instance.call(memory=memory, user_message=query)
            return {
                "success": True,
                "agent_name": self.agent_name,
                "query": query,
                "response": agent_response,
            }, memory

        except Exception as e:
            return {
                "success": False,
                "agent_name": self.agent_name,
                "query": query,
                "error": str(e),
                "traceback": traceback.format_exc()
            }, memory

    def initialize(self):
        """
        Devuelve la configuración de la herramienta para el framework de OpenAI function calling.

        Returns:
            list: Lista con la configuración de la herramienta
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
        Ejecuta la herramienta específica con los argumentos proporcionados.

        Args:
            tool_name (str): Nombre de la herramienta a ejecutar
            payload (dict): Argumentos para la herramienta

        Returns:
            dict: Respuesta de la herramienta en formato estándar
        """
        # Mapeo entre nombres y funciones
        name_to_func = {self.agent_name + "_tool": self.agent_name + "_tool"}
        func_key = name_to_func.get(tool_name)
        if not func_key:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({
                    "error": f"Herramienta '{tool_name}' no encontrada en {self.toolbox_name}"
                })
            }, memory

        try:
            payload['memory'] = memory
            result, memory = self.sub_tools[func_key](**payload)
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(result, ensure_ascii=False)
            }, memory

        except Exception as e:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({
                    "error": f"Error ejecutando {tool_name}: {str(e)}",
                    "traceback": traceback.format_exc()
                })
            }, memory

# Ejemplo de uso
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    # Importar el agente de ejemplo (asumiendo que está disponible)
    # from tu_modulo import ManagerAgent

    # Crear una instancia del agente que queremos consultar
    # consulted_agent = ManagerAgent()

    # Crear la herramienta de consulta
    # consultation_tool = AgentConsultationToolbox(
    #     agent_instance=consulted_agent,
    #     agent_name="SearchAgent"
    # )

    # Ejemplo de uso de la herramienta
    print("=== Configuración de la herramienta para OpenAI ===")
    # tools_config = consultation_tool.initialize()
    # print(json.dumps(tools_config, indent=2, ensure_ascii=False))

    print("\n=== Ejemplo de consulta al agente ===")


    # payload = {
    #     "query": "¿Cuál es la capital de Francia?",
    #     "context": "Necesito información básica de geografía"
    # }
    # response = consultation_tool.call("consult_agent", payload)
    # print("Respuesta:", json.dumps(json.loads(response["content"]), indent=2, ensure_ascii=False))

    # Ejemplo sin agente real para mostrar la estructura
    class MockAgent:
        def initialize(self, memory):
            return memory

        def call(self, memory, user_message):
            return memory, f"Respuesta simulada para: {user_message}"


    mock_agent = MockAgent()
    consultation_tool = AgentCommunicationToolbox(
        agent_instance=mock_agent,
        agent_name="MockAgent"
    )

    print("=== Configuración de herramientas ===")
    tools_config = consultation_tool.initialize()
    print(json.dumps(tools_config, indent=2, ensure_ascii=False))

    print("\n=== Ejemplo con agente simulado ===")
    payload = {
        "query": "¿Cómo estás?",
        "context": "Saludo simple"
    }
    response = consultation_tool.call("consult_agent", payload)
    print("Respuesta:", json.dumps(json.loads(response["content"]), indent=2, ensure_ascii=False))