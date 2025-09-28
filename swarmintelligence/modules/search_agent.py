import json
from eigenlib.genai.llm_client import LLMClient
from swarmintelligence.modules.web_search_toolbox import WebSearchToolbox
from eigenlib.genai.memory import Memory
from swarmintelligence.modules.memory_manager import MemoryManager

class SearchAgent:
    def __init__(self):
        # CONFIGURATION
        self.id = 'SEARCH_AGENT'
        self.memory_file = f'./data/raw/{self.id}_agent_memory.pkl'
        self.model = 'gpt-4.1'
        self.client = 'oai_1'
        self.temperature = 1
        self.tool_choice = 'auto'
        self.reasoning_effort = None
        self.use_steering = False
        self.memory_threshold = 10000

        # UTILS
        self.mm = MemoryManager()

        # TOOLS
        sp_tool = WebSearchToolbox(default_max_results=5, default_region="wt-wt")
        self.toolboxes = [sp_tool]

    def initialize(self, memory=Memory()):
        # TOOL INITIALIZATION
        tools_map = {}
        tools_config = []
        for tb in self.toolboxes:
            tools_dicts = tb.initialize()
            for t in tools_dicts:
                tools_map[t['function']['name']] = tb
                tools_config.append(t)
        self.tools_map = tools_map
        self.tools_config = tools_config

        # LANGUAGE MODEL INITIALIZATION
        self.LLM = LLMClient(client=self.client)
        return memory

    def call(self, memory=None, user_message=None, **kwargs):
        memory.log(role='system', modality='text', content=self.system_prompt_template(), steering=True, channel=self.id)
        memory.log(role='user', modality='text', content=user_message, channel=self.id)
        while True:
            answer = self.LLM.run(self.mm.get(memory.history, user_message, self.id), model=self.model, temperature=self.temperature, reasoning_effort=self.reasoning_effort, tools_config=self.tools_config, response_format=None, tool_choice=self.tool_choice)
            if type(answer) == dict:
                print('TOOL CALL: ', str(answer)[0:1000])
                memory.log(role='assistant', modality='tool_call', content = answer, channel = self.id)
                tool_answer, memory = self._tool_call(answer, memory)
                memory.log(role='tool', modality='tool_result', content=tool_answer, channel=self.id)
                print('TOOL: ', tool_answer['tool_call_result'][0:1000])
                print('------------------------------------------------------------------------------------------------')
            else:
                memory.log(role='assistant', modality='text', content=answer, channel = self.id)
                break
        return memory, answer

    def _tool_call(self, query, memory):
        call_tool_name = query['function']['name']
        call_toolbox = self.tools_map[call_tool_name]
        call_args = json.loads(query['function']['arguments'])
        tool_response, memory = call_toolbox.call(tool_name=call_tool_name, payload=call_args, memory=memory)
        return {'tool_call_id': query['id'], 'tool_call_function_name': query['function']['name'], 'tool_call_result': json.dumps(tool_response)}, memory

    def system_prompt_template(self):
        system_prompt = f"""
# CONTEXTO
Vas a actuar en modo agente de búsquedas en internet.

Tu misión es realizar búsquedas de urls en la herramienta y posteriormente abrirlas para extraer el contenido relevante de la busqueda.

Responde con el resultado de la búsqueda.
"""
        return system_prompt

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = SearchAgent()
    memory = agent.initialize()
    memory, answer = agent.call(memory=memory, user_message='Busca en internet la página de wikipedia del F22 y dime cuanto empuje tienen sus motores.')
