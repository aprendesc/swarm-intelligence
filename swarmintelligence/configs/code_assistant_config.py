from swarmintelligence.configs.test_config import config as test_config
import os

"""test_assistant/code_assistant"""
########################################################################################################################
base_path = f'C:\\Users\\{os.environ["USERNAME"]}\\Desktop\\proyectos'
target_project_folder = 'swarm-intelligence'
########################################################################################################################
target_project_root = os.path.join(base_path, target_project_folder)
from swarmintelligence.modules.get_project_map import GetProjectMap
flat_map, tree_map = GetProjectMap().run(target_project_root)
assistant_name = 'software_developer_assistant'
"""Tools Setup"""
if True:
    import sys
    import os
    sys.path.extend([os.path.join(base_path, 'swarm-automations')])
    from swarmautomations.modules.main_class_tool_adapter import MainClassToolAdapter
    from swarmautomations.main import MainClass as ToolsMainClass
    # CODE INTERPRETER TOOL SETUP
    tool_name = 'code_interpreter'
    tool_description = """Code interpreter for expert software development in the environment of the project."""
    default_config = {'interpreter_path': os.path.join(base_path, target_project_folder, '.venv\Scripts\python.exe')}
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
    tool_description = "Makes a deep web search and gets the results."
    default_config = {
        'summarize': True,
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
            "description": "Maximum number of results to get with a maximum of 20. Higher number for a deeper search. Default 10",
            "required": True,
        },
    ]
    ws_tool = MainClassToolAdapter(ToolsMainClass({}).intelligent_web_search, tool_name=tool_name, tool_description=tool_description, default_config=default_config ,tool_args=tool_args)

    # SOURCE PARSE TOOL
    tool_name = 'sources_parser_and_summarizer'
    tool_description = "Tool made for parsing and building summaries of documents, pdf, websites... Admits urls to the web or local paths to local documents. It also includes the functionality of uploading the content to notion."
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
            "description": "Local path or URL of the source that will be parsed summarized and uploaded.",
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

    # LOCAL FILE OPERATIONS TOOL
    tool_name = 'file_operations_tools'
    tool_description = ("Tool for basic file operations. Supports reading the content of a file "
        "or writing text into a file. Accepts both local file paths and temporary files. "
        "Returns the read content or a confirmation message depending on the mode.")
    default_config = {
        'file_path': '',
        'mode': 'read_file',
        'content': '',
    }
    tool_args = [
        {
            "name": "file_path",
            "type": "string",
            "description": "Full path to the file to read or write.",
            "required": True,
        },
        {
            "name": "mode",
            "type": "string",
            "enum": ["read_file", "write_file"],
            "description": "Operation mode: 'read_file' to read the file, 'write_file' to overwrite the file with provided content.",
            "required": True,
        },
        {
            "name": "content",
            "type": "string",
            "description": "Content to write to the file. Required if mode is 'write_file'. 'no_content' when mode is 'read_file'.",
            "required": False,
        },
    ]
    fo_tool = MainClassToolAdapter(ToolsMainClass({}).local_file_operations_tools, tool_name=tool_name, tool_description=tool_description, default_config=default_config ,tool_args=tool_args)

    # GET PROJECT MAP TOOL
    tool_name = 'get_project_map'
    tool_description = ("Tool for scanning and mapping the file structure of the project directory. "
        "It traverses all subdirectories starting from the root dir and returns a list of file paths "
        "Useful for exploring the project."
        "When launched it simply gets the current structure of files and folders of the project. No arguments needed.")
    default_config = {
        'root_path': target_project_root,
    }
    tool_args = []
    pm_tool = MainClassToolAdapter(ToolsMainClass({}).get_project_map, tool_name=tool_name, tool_description=tool_description, default_config=default_config ,tool_args=tool_args)

tools = {
    'intelligent_web_search': ws_tool,
    'sources_parser_and_summarizer': sp_tool,
    'code_interpreter': ci_tool,
    'file_operations_tools': fo_tool,
    'get_project_map': pm_tool,
}
update_dict = {
    'hypothesis': """Software developer assistant that can be used as a tool for developing advanced software.""",
    # INITIALIZE
    'assistant_name': assistant_name,
    'agent_model': 'o3',
    'agent_reasoning_effort': 'high',
    'temperature': 1,
    'tools_dict': tools,
    'tool_choice': 'auto',
    #INFERENCE
    'agent_context': f"""
Y
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
