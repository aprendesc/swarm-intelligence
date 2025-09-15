
from dotenv import load_dotenv
load_dotenv()
from swarmintelligence.modules.general_agent import GeneralAgent
agent = GeneralAgent()
memory = agent.initialize()
memory, answer = agent.call(memory=memory, user_message='Hola!')
