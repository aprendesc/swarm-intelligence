from eigenlib.genai.llm_client import LLMClient
from eigenlib.genai.memory import Memory
import json

class GeneralSynthUser:
    def __init__(self, system_prompt=None, structured_query_prompt=None, model='o3', tools=[], eval_prompt=None, query_format=None, eval_format=None):
        self.id = 'GENERAL_SYNTH_USER'
        self.system_prompt = system_prompt
        self.structured_query_prompt = structured_query_prompt
        self.model = model
        self.client = 'oai_2'
        self.temperature = 1
        self.tool_choice = 'auto'
        self.use_steering = True
        self.tools = tools
        self.eval_prompt = eval_prompt
        self.query_format = query_format
        self.eval_format = eval_format

    def initialize(self, memory=Memory(), state=None):
        # TOOLS SETUP
        self.tools_dict = {t().tool_name: t() for t in self.tools}
        # SYSTEM
        self.LLM = LLMClient(client=self.client)
        memory.log(role='system', modality='text', content=self.system_prompt, channel=self.id)
        return memory

    def call(self, memory=None, agent_message=None, **kwargs):
        # ANSWER
        memory.log(role='user', modality='text', content=agent_message, channel=self.id)
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
        memory.log(role='system', modality='text', content=self.structured_query_prompt, steering=True, channel=self.id)
        answer = self.LLM.run(self._memory_manager(memory.history), model=self.model, temperature=self.temperature, response_format=self.query_format, tool_choice=self.tool_choice)
        answer = eval(answer.model_dump_json())
        return memory, answer['query'], answer['hint']

    def eval(self, memory=None, agent_message=None, **kwargs):
        memory.log(role='system', modality='text', content=self.eval_prompt, steering=True, channel=self.id)
        memory.log(role='user', modality='text', content=agent_message, steering=True, channel=self.id)
        if kwargs.get('update', True):
            answer = self.LLM.run(self._memory_manager(memory.history), model=self.model, temperature=self.temperature, tools_dict=None, response_format=self.eval_format, tool_choice=None)
            answer = eval(answer.model_dump_json())
        else:
            answer = {'reasoning': kwargs['user_message'], 'score': kwargs['score']}
        return memory, answer['reasoning'], answer['score']

    def _tool_call(self, query):
        tool_result = self.tools_dict[query['function']['name']].call(json.loads(query['function']['arguments']))
        return {'tool_call_id': query['id'], 'tool_call_function_name': query['function']['name'], 'tool_call_result': tool_result}

    def _memory_manager(self, history):
        history = history[history['channel'] == self.id]
        if not self.use_steering:
            history = history[history['steering'] == False]
        return history



