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




from eigenlib.utils.nano_net import NanoNetClass

class OSLLMClientClass:
    def __init__(self, master_address='tcp://95.18.166.44:5005'):
        password = 'youshallnotpass'
        ################################################################################################################
        self.client_node = NanoNetClass()
        self.client_node.launch_node(node_name='client_node', node_method=None, master_address=master_address, password=password, delay=1)

    def run(self, history):
        result = self.client_node.call(address_node="phi_4_node", payload={'history': history})
        return result

LLM = OSLLMClientClass()
answer = LLM.run([{'role': 'user', 'content': 'Actua como un simulador de fisicas: si tengo una caja con pelotas, una de adhesivo, otra de helio otra de plomo y otra de neutronio, en t0 la caja esta dada la vuelta y con las pelotas en el fondo, cual es el estado en t10 segundos? '}])
print(answer)


from eigenlib.utils.project_setup import ProjectSetupClass
ProjectSetupClass(project_folder='swarm-intelligence')

from eigenlib.LLM.llm_client import LLMClientClass
from eigenlib.LLM.episode import EpisodeClass

################################################################################################################
episode = EpisodeClass()
episode.log(channel='user', modality='text', content='Cuenta de 0 a 10', agent_id='Q')
answer = LLMClientClass(model='gpt-5-chat', temperature=1).run(episode=episode, agent_id='Q')
print(answer)
answer = LLMClientClass(model='o3', temperature=1).run(episode=episode, agent_id='Q')
print(answer)
answer = LLMClientClass(model='claude-3_v1', temperature=1).run(episode=episode, agent_id='Q')
print(answer)
answer = LLMClientClass(model="oss_phi_4", temperature=1).run(episode=episode, agent_id='Q')
print(answer)