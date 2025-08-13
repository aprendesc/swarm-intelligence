from swarmintelligence.configs.test_config import test_config

"""test_assistant/general_purpose"""
assistant_name = 'general_purpose_assistant'
from swarmintelligence.modules.web_search_tool import WebSearchTool
tools = {'intelligent_web_search': WebSearchTool()}
update_dict = {
    'hypothesis': """General purpose assistant.""",
    # INITIALIZE
    'assistant_name': assistant_name,
    'agent_model': 'o3',
    'agent_reasoning_effort': 'high',
    'temperature': 1,
    'tools_dict': tools,
    'tool_choice': 'auto',
    #INFERENCE
    'agent_context': """""",
    'agent_instructions': "You are a very precise and obedient assistant.",
    'steering': None,
    'img': None,
    'user_message': 'Ejecuta el codigo de factorial de 12 y dime el resultado.',
}
gp_assistant_config = test_config | update_dict
########################################################################################################################

"""test_assistant/code_assistant"""
from swarmintelligence.modules.get_project_map import GetProjectMap
flat_map, tree_map = GetProjectMap().run(r'C:\Users\AlejandroPrendesCabo\Desktop\proyectos\swarm-intelligence')
assistant_name = 'software_developer_assistant'
from swarmintelligence.modules.code_interpreter_tool import CodeInterpreterToolClass
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
code_assistant_config = test_config | update_dict
########################################################################################################################

"""test_assistant/project_manager_assistant"""
assistant_name = 'project_manager_assistant'
from swarmintelligence.modules.custom_assistant_tool import CustomAssistantTool
tools = {
    'software_developer_assistant': CustomAssistantTool(code_assistant_config, tool_description='This tool is a software engineer from your team as manager.'),
}
update_dict = {
    'hypothesis': """This assistant is a project manager..""",
    # INITIALIZE
    'assistant_name': assistant_name,
    'agent_model': 'o3',
    'agent_reasoning_effort': 'high',
    'temperature': 1,
    'tools_dict': tools,
    'tool_choice': 'auto',
    # INFERENCE
    'agent_context': """You are an expert software project manager assistant with the responsibilities of:
Step 1: Debate with the user to define scope, milestones, ideas, and make a plan.
Stage 2: When the contract with the user and the plan is ready, start working with the developer tools.
Stage 3: Manage the team of developers as Tools: Query the developer with tasks. Oversee their results, discuss the results...
Stage 4: Report and deliver the results to the user as an answer, delivering the resulting code, paying detailed attention to the user's requests and how he wants it etc..
    """,
    'agent_instructions': "INSTRUCTIONS: All your team is made of different AI tools that you can query when you need it. Work with your team(tools) to deliver a solution to user's needs paying attention to every need and requests and ensuring you (the team) deliver the requirements.",
    'steering': None,
    'img': None,
    'user_message': 'Quiero obtener un codigo que obtenga en ascii la figura de una montaña printeada por pantalla.',
}
project_manager_assistant = test_config | update_dict
########################################################################################################################


