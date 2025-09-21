from eigenlib.genai.llm_client import LLMClient
from eigenlib.genai.memory import Memory
import json

class GeneralAgent:
    def __init__(self, system_prompt=None, model='o3', client='oai_2', temperature=1, tools=[]):
        self.id = 'GENERAL_AGENT'
        self.system_prompt = system_prompt
        self.model = model
        self.client = client
        self.temperature = temperature
        self.tool_choice = 'auto'
        self.use_steering = True
        self.tools = tools

    def initialize(self, memory=Memory(), agent_config=None):
        self.tools_dict = {t.tool_name: t for t in self.tools}
        self.LLM = LLMClient(client=self.client)
        memory.log(role='system', modality='text', content=self.system_prompt, channel=self.id)
        return memory

    def call(self, memory=None, user_message=None, steering=None, **kwargs):
        if steering is not None:
            steering = 'Instrucciones para responder: ' + steering
            print('HINT: ', steering)
        memory.log(role='system', modality='text', content=steering, steering=True, channel=self.id)
        memory.log(role='user', modality='text', content=user_message, channel=self.id)
        while True:
            answer = self.LLM.run(self._memory_manager(memory.history), model=self.model, temperature=self.temperature, tools_dict=self.tools_dict, response_format=None, tool_choice=self.tool_choice)
            if type(answer) == dict:
                print('TOOL CALL: ', str(answer)[0:1000])
                memory.log(role='assistant', modality='tool_call', content = answer, channel = self.id)
                tool_answer = self._tool_call(answer)
                memory.log(role='tool', modality='tool_result', content=tool_answer, channel=self.id)
                print('TOOL: ', tool_answer['tool_call_result'][0:1000])
                print('------------------------------------------------------------------------------------------------')
            else:
                memory.log(role='assistant', modality='text', content=answer, channel = self.id)
                break
        return memory, answer

    def _tool_call(self, query):
        tool_result = self.tools_dict[query['function']['name']].call(json.loads(query['function']['arguments']))
        return {'tool_call_id': query['id'], 'tool_call_function_name': query['function']['name'], 'tool_call_result': tool_result}

    def _memory_manager(self, history):
        history = history[history['channel'] == self.id]
        if not self.use_steering:
            history = history[history['steering'] == False]
        return history

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = GeneralAgent()
    memory = agent.initialize()
    memory, answer = agent.call(memory=memory, user='Hazme un EDA basico de la tabla de escandallos.')
    print(answer)