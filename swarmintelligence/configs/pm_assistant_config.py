from swarmintelligence.configs.test_config import config as test_config
from swarmintelligence.configs.swarm_intelligence_code_assistant_config import config

"""test_assistant/project_manager_assistant"""
assistant_name = 'project_manager_assistant'
from swarmintelligence.modules.custom_assistant_tool import CustomAssistantTool
tools = {
    'software_developer_assistant': CustomAssistantTool(config, tool_description='This tool is a software engineer from your team as manager.'),
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


