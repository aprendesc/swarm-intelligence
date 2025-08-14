from swarmintelligence.configs.test_config import config as test_config

"""test_assistant/code_assistant"""
from swarmintelligence.modules.get_project_map import GetProjectMap
flat_map, tree_map = GetProjectMap().run(r'C:\Users\AlejandroPrendesCabo\Desktop\proyectos\swarm-intelligence')
assistant_name = 'software_developer_assistant'
from swarmintelligence.modules.code_interpreter_tool import CodeInterpreterToolClass
from swarmintelligence.modules.web_search_tool import WebSearchTool
interpreter_path = r"C:\Users\AlejandroPrendesCabo\Desktop\proyectos\swarm-intelligence\.venv\Scripts\python.exe"
tools = {
    'code_interpreter': CodeInterpreterToolClass(interpreter_path=interpreter_path, path_folders=[
        r"C:\Users\AlejandroPrendesCabo\Desktop\proyectos\swarm-intelligence",
        r"C:\Users\AlejandroPrendesCabo\Desktop\proyectos\eigenlib"]),
    'intelligent_web_search': WebSearchTool(),
}
update_dict = {
    'hypothesis': """Software developer assistant that can be used as a tool for developing advanced software.""",
    # INITIALIZE
    'assistant_name': assistant_name,
    'agent_model': 'gpt-5-mini',
    'agent_reasoning_effort': 'high',
    'temperature': 1,
    'tools_dict': tools,
    'tool_choice': 'auto',
    #INFERENCE
    'agent_context': f"""
# PROJECT MAP

{flat_map}
    """,
    'agent_instructions': """""",
    'steering': """
# INSTRUCTIONS:
* You are a high skilled software developer expert in developing clean, efficient, high quality code and solutions for the user's project.
* Answer always with full solutions.
* Use any tool needed. You can use the code interpreter to solve the user's requests and instructions.
* You can search the internet using the intelligent_web_search tool to check for information, documentation, browse webs etc...
* User can't see tool outputs, you must deliver every relevant information in your answer.
* Before taking action always plan the best steps to solve the problem, you can use the tools as many times as you need and update your plan based on the new information gathered until the goal is achieved.
""",
    'img': None,
    'user_message': 'Ejecuta el codigo de factorial de 12 y dime el resultado.',
}
config = test_config | update_dict
########################################################################################################################
