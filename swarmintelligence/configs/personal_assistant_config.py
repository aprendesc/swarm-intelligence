from swarmintelligence.configs.test_config import config as test_config

"""test_assistant/code_assistant"""
from swarmintelligence.modules.get_project_map import GetProjectMap
flat_map, tree_map = GetProjectMap().run(r'C:\Users\AlejandroPrendesCabo\Desktop\proyectos\swarm-intelligence')
assistant_name = 'personal_assistant'
"""Tools Setup"""
if True:
    import sys
    import os
    base_path = f'C:/Users/{os.environ["USERNAME"]}/Desktop/proyectos'
    sys.path.extend([os.path.join(base_path, 'swarm-automations')])
    from swarmautomations.modules.main_class_tool_adapter import MainClassToolAdapter
    from swarmautomations.main import MainClass as ToolsMainClass
    # CODE INTERPRETER TOOL SETUP
    tool_name = 'code_interpreter'
    tool_description = """Code interpreter for expert software development in the environment of the project."""
    default_config = {}
    tool_args = [
        {
            "name": "programming_language", "type": "string",
            "enum": ["python", "bash"],
            "description": "Language of the code to execute.",
            "required": True,
        },
        {
            "name": "code", "type": "string",
            "description": "Code that will be executed in the code interpreter.",
            "required": True,
        },
    ]
    ci_tool = MainClassToolAdapter(ToolsMainClass({}).code_interpreter, tool_name=tool_name, tool_description=tool_description, default_config=default_config, tool_args=tool_args)

    # WEB SEARCH TOOL
    tool_name = 'intelligent_web_search'
    tool_description = """Tool that makes a search query in google, extracts the top n result urls returns the relevant information from those sources based on the query."""
    default_config = {
        'summarize': False,
    }
    tool_args = [
        {
            "name": "query",
            "type": "string",
            "description": "Text of the query for the web search, it admits complex and simple queries.",
            "required": True,
        },
        {
            "name": "num_results",
            "type": "integer",
            "description": "Maximum number of results to get with a maximum of 20. Higher number for a deeper search. Default 5",
            "required": True,
        },
    ]
    ws_tool = MainClassToolAdapter(ToolsMainClass({}).intelligent_web_search, tool_name=tool_name, tool_description=tool_description, default_config=default_config ,tool_args=tool_args)

    # SOURCE PARSE TOOL
    tool_name = 'sources_parser_and_summarizer'
    tool_description = """Tool made for parsing and building summaries of sources, from pdf to web sources. 
Admits urls to the web or local paths to local documents.
The results are uploaded into notion.
"""
    default_config = {
        'parse': True,
        'to_notion': True,
        'summarize': True,
        'summarizer_notion_page': '2432a599e985804692b7d6982895a2b2',
    }
    tool_args = [
        {
            "name": "source_path_or_url",
            "type": "string",
            "description": "Path or URL of the source that will be parsed summarized and uploaded.",
            "required": True,
        },
        {
            "name": "n_sections",
            "type": "integer",
            "description": "Number of sections of the summary. Each section is a paragraph of the summary. Default 3.",
            "required": True,
        },
        {
            "name": "to_notion",
            "type": "boolean",
            "description": "True to send the summary to notion. Default: True",
            "required": True,
        },
        {
            "name": "summarize",
            "type": "boolean",
            "description": "True to summarize the source instead of parsing the raw source. Default: True",
            "required": True,
        },
    ]
    sp_tool = MainClassToolAdapter(ToolsMainClass({}).sources_parser_and_summarizer, tool_name=tool_name, tool_description=tool_description, default_config=default_config ,tool_args=tool_args)

tools = {
    'code_interpreter': ci_tool,
    'intelligent_web_search': ws_tool,
    'sources_parser_and_summarizer': sp_tool
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
    'agent_context': f"""You are a personal assistant that helps the user with any request he makes.""",
    'agent_instructions': """""",
    'steering': """
# INSTRUCTIONS:
* You have access to several tools to search, summarize info, run code etc... that you can use when needed.
* Before taking action always plan the best steps to solve the query.
* Always confirm the plan with the user before taking action that can take time and work.
* Give always short and direct final answer with condensed relevant information unless you are explicitly required to give long answers.
""",
    'img': None,
    'user_message': 'Ejecuta el codigo de factorial de 12 y dime el resultado.',
}
config = test_config | update_dict
########################################################################################################################
