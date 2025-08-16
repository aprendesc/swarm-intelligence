import os
import sys

"""test_assistant/code_assistant"""
assistant_name = 'software_developer_assistant'
########################################################################################################################
from swarmintelligence.configs.test_config import config as test_config
base_path = f'C:\\Users\\{os.environ["USERNAME"]}\\Desktop\\proyectos'
target_project_folder = 'swarm-intelligence'
target_path_dirs = [
                        os.path.join(base_path, target_project_folder),
                        os.path.join(base_path, 'eigenlib')
                ]
########################################################################################################################
target_project_name = target_project_folder.replace('-', '')
target_project_cwd = os.path.join(base_path, target_project_folder)
"""Tools Setup"""
if True:
    sys.path.extend([os.path.join(base_path, 'swarm-automations')])
    from swarmautomations.modules.main_class_tool_adapter import MainClassToolAdapter
    from swarmautomations.main import MainClass as ToolsMainClass
    # CODE INTERPRETER TOOL SETUP
    tool_name = 'code_interpreter'
    tool_description = """Code interpreter for expert software development in the environment of the project."""
    default_config = {
        'interpreter_launcher': os.path.join(target_project_cwd, '.venv\Scripts\python.exe'),
        'interpreter_cwd': target_project_cwd,
        'interpreter_path_dirs': target_path_dirs,
    }
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
        "Returns the read content or a confirmation message depending on the mode."
        "The basic structure of the project and developing libraries is: "
        f"""
# EIGENLIB LIBRARY
* This is a general purpose library that can be used in any project and contains modules and utilities useful for different projects.
../eigenlib/eigenlib/image # Modules useful for image manipulation.
../eigenlib/eigenlib/audio # Modules useful for audio manipulation.
../eigenlib/eigenlib/ML # Modules useful for building modular machine learning models.
../eigenlib/eigenlib/LLM # Modules useful for developing gen AI LLM applications.
../eigenlib/eigenlib/utils # Contain low level utilities for building projects. Very important, contains many low level modules to build projects.

# {target_project_name.upper()} LIBRARY
./data/raw #Storage of raw sources.
./data/curated #Storage of curated sources. Used as feature store.
./data/processed # Storage of processed sources.
./doc/ # Documentation of the project.
./img/ 
./models/ # Storage of machine Learning models
./scripts/ # Utils scripts for the project.
./{target_project_name}/main.py # Main script of the project.
./{target_project_name}/modules # All the modules that are inside the project are here.
./{target_project_name}/development # Directory with files under development, safe area.
./{target_project_name}/configs # Files that builds the configuration files for the main class.
./tests/test_main.py #T est module of the main script.
./tests/modules # Test for testing the modules. One test for each module in the project folder.
        """)
    default_config = {
        'files_cwd': target_project_cwd,
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
    tool_name = 'get_files_map'
    tool_description = ("Tool for scanning and mapping the file structure of a given directory. "
        "It traverses all subdirectories starting from the root dir and returns a list of file paths "
        "Useful for exploring projects."
        "To access other projects do: ../name-of-project/name_of_folder, eg: ../eigenlib/utils"
        "When launched it simply gets the current structure of files and folders of the project. No arguments needed.")
    default_config = {
        'map_base_path': target_project_cwd,
        'map_root_dir': './',
    }
    tool_args = [
        {
            "name": "map_root_dir",
            "type": "string",
            "description": "Root directory to extract the tree of files and subdirectories. Default '.'",
            "required": True,
        },
    ]
    pm_tool = MainClassToolAdapter(ToolsMainClass({}).get_files_map, tool_name=tool_name, tool_description=tool_description, default_config=default_config ,tool_args=tool_args)

    # GOOGLE SEARCH TOOL ADAPTER
    tool_name = 'google_search'
    tool_description = "Tool that performs a Google search and returns a list with the resulting URLs."
    default_config = {
        'num_results': 10,
    }
    tool_args = [
        {
            "name": "query",
            "type": "string",
            "description": "Text of the query for the web search.",
            "required": True,
        },
        {
            "name": "num_results",
            "type": "integer",
            "description": "Maximum number of results to retrieve (max 20). Default 10.",
            "required": False,
        },
    ]
    gs_tool = MainClassToolAdapter(ToolsMainClass({}).google_search, tool_name=tool_name, tool_description=tool_description, default_config=default_config, tool_args=tool_args, )

    # BROWSE URL TOOL ADAPTER
    tool_name = 'browse_url'
    tool_description = "Tool that browses a list of URLs and extracts the content or a summary for each one."
    default_config = {
        'summarize_search': False,
    }
    tool_args = [
        {
            "name": "urls",
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of URLs to browse.",
            "required": True,
        },
        {
            "name": "query",
            "type": "string",
            "description": "Original user query (used only when summarising).",
            "required": False,
        },
        {
            "name": "summarize_search",
            "type": "boolean",
            "description": "True to summarise the browsed content. Default False.",
            "required": False,
        },
    ]
    br_tool = MainClassToolAdapter(ToolsMainClass({}).browse_url, tool_name=tool_name, tool_description=tool_description, default_config=default_config, tool_args=tool_args)

tools = {
    #'intelligent_web_search': ws_tool,
    'google_search': gs_tool,
    'browse_url': br_tool,
    'sources_parser_and_summarizer': sp_tool,
    'code_interpreter': ci_tool,
    'file_operations_tools': fo_tool,
    'get_files_map': pm_tool,
}
update_dict = {
    # -------- META --------------------------------------------------------------------
    'hypothesis': """Software developer assistant that can be used as a tool for developing advanced software.""",
    'lang': 'eng',

    # -------- INITIALISATION ----------------------------------------------------------
    'assistant_name': assistant_name,
    'user_model': 'o3',
    'agent_model': 'o3',
    'eval_model': 'o3',
    'user_reasoning_effort': 'medium',
    'agent_reasoning_effort': 'high',
    'eval_reasoning_effort': 'low',
    'temperature': 1.0,
    'tools_dict': tools,
    'tool_choice': 'auto',

    # -------- GENERAL RUNTIME SETTINGS ------------------------------------------------
    'use_cloud': False,
    'use_wandb': False,
    'n_samples': 3,
    'n_thread': 8,
    'use_guidance': True,

    # -------- VDB / SEEDS -------------------------------------------------------------
    'raw_sources': [],
    'seeds_dataset_name': assistant_name + '_SEEDS',
    'seeds_chunking_threshold': 900,
    'vdb_name': assistant_name + '_VDB',
    'vdb_chunking_threshold': 150,

    # -------- GENERATIVE SETTINGS -----------------------------------------------------
    'gen_input_dataset_name': assistant_name + '_SEEDS',
    'gen_output_dataset_name': assistant_name + '_GEN',
    'hist_output_dataset_name': assistant_name + '_GEN_HIST',
    'gen_static_user': False,
    'gen_max_iter': 1,
    'gen_n_epoch': 10,
    'gen_use_agent_steering': True,
    'del_steering': True,
    'history': {},

    # -------- TRAIN / FINE-TUNE -------------------------------------------------------
    'ft_dataset_name': assistant_name + '_FT',
    'perc_split': 0.2,
    'run_ft': False,
    'n_epochs': 1,
    'ft_model': 'o3-mini',

    # -------- EVAL --------------------------------------------------------------------
    'eval_input_dataset_name': assistant_name + '_GEN',
    'eval_output_dataset_name': assistant_name + '_EVAL',
    'eval_hist_output_dataset_name': assistant_name + '_HIST_EVAL',
    'eval_static_user': True,
    'eval_max_iter': 1,
    'eval_use_agent_steering': False,

    # -------- TEXT CONTEXTS / INSTRUCTIONS -------------------------------------------
    'user_context': """
# CONTEXT:
You are the user who interacts with a highly capable software-developer assistant.
You ask questions, request implementations and review existing code.
    """,
    'user_instructions': """
# INSTRUCTIONS (USER):
Provide clear requirements, constraints and expectations for the code you want to be written or analysed.
    """,
    'agent_context': f"""
# CONTEXT:
You are an advanced AI software developer that helps the user to work in his project. 
Project name: {target_project_folder}
    """,
    'agent_instructions': """""",
    'eval_instructions': """
# NEW INSTRUCTIONS:
Given the conversation so far, evaluate the assistant response on correctness and helpfulness (0–10).
    """,

    # -------- STEERING / TEST MESSAGE -------------------------------------------------
    'steering': """
# INSTRUCTIONS:
* You are a high skilled software developer expert in developing clean, efficient, high quality code and solutions for the user's project.
* Answer always with full solutions.
* Use any tool needed. You can use the code interpreter to solve the user's requests and instructions.
* You can search the internet using the intelligent_web_search tool to check for information, documentation, browse webs etc...
* User can't see tool outputs, you must deliver every relevant information in your answer.
* Before taking action always plan the best steps to solve the problem, you can use the tools as many times as you need and update your plan based on the new information gathered until the goal is achieved.
    """,

    # -------- MISC --------------------------------------------------------------------
    'img': None,
    'user_message': 'Lets work on improving fine tuning of models. First of all, identify in eigenlib the file llm_client',
}
########################################################################################################################
