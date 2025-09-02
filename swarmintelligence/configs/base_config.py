from swarmintelligence.modules.server_tool import ServerTool

use_tools = True

class Config:
    def __init__(self):
        ########################################################################################################################
        assistant_name = 'software_developer_assistant'
        environments = ["jedipoc", "swarmintelligence", "swarmautomations", 'swarmml', 'swarmcompute', 'eigenlib']
        address_node = 'project_dev_node'
        target_project_folder = 'swarm-intelligence'
        user_model = 'o3'
        agent_model = 'o3'
        eval_model = 'o3'
        user_reasoning_effort = 'medium'
        agent_reasoning_effort = 'high'
        eval_reasoning_effort = 'low'
        temperature = 1.0
        use_cloud = False
        use_wandb = False
        n_thread = 8
        use_guidance = True
        lang = 'eng'
        ########################################################################################################################
        environ_arg = [{
            "name": "selected_project",
            "type": "string",
            "description": "This argument allows to select the project to work with. Must be specified by user.",
            "enum": environments,
            "required": True,
        }]

        """Tools Setup"""
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
                            "description": "Code that will be executed in the code interpreter. Use prints to get the relevant information you want to gather from executions.",
                            "required": True,
                        },
                    ] + environ_arg
        ci_tool = ServerTool('code_interpreter', tool_name=tool_name, tool_description=tool_description, default_config=default_config, tool_args=tool_args)

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
                    ] + environ_arg
        sp_tool = ServerTool('sources_parser_and_summarizer', tool_name=tool_name, tool_description=tool_description, default_config=default_config, tool_args=tool_args)

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

        # PROJECTS STRUCTURE
        Every projects from the given has the structure:
        ./data/raw #Storage of raw sources.
        ./data/curated #Storage of curated sources. Used as feature store.
        ./data/processed # Storage of processed sources.
        ./doc/ # Documentation of the project.
        ./img/ 
        ./models/ # Storage of machine Learning models
        ./scripts/ # Utils scripts for the project.
        ./projectmodule/main.py # Main script of the project.
        ./projectmodule/modules # All the modules that are inside the project are here.
        ./projectmodule/development # Directory with files under development, safe area.
        ./projectmodule/configs # Files that builds the configuration files for the main class.
        ./tests/test_main.py #T est module of the main script.
        ./tests/modules # Test for testing the modules. One test for each module in the project folder.

        projectmodule is the name of the module (eg, swarmintelligence)
            """)
        default_config = {}
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
                            "enum": ["read_file", "write_file", "replace"],
                            "description": "Operation mode: 'read_file' to read the file, 'write_file' to overwrite the file with provided content.",
                            "required": True,
                        },
                        {
                            "name": "content",
                            "type": "string",
                            "description": "Content to write to the file. 'no_content' when mode is 'read_file'. Required only in 'write_file' or 'replace' mode.",
                            "required": False,
                        },
                        {
                            "name": "content_to_replace",
                            "type": "string",
                            "description": "Content to be replaced by the content argument. You must include *exactly* the string to be replaced. Required only in 'replace' mode.",
                            "required": False,
                        },

                    ] + environ_arg
        fo_tool = ServerTool('local_file_operations_tools', tool_name=tool_name, tool_description=tool_description, default_config=default_config, tool_args=tool_args)

        # GET FILES MAP TOOL
        tool_name = 'get_files_map'
        tool_description = ("Tool for scanning and mapping the file structure of a given directory. "
                            "It traverses all subdirectories starting from the root dir and returns a list of file paths "
                            "Useful for exploring projects."
                            "To access other projects do: ../name-of-project/name_of_folder, eg: ../eigenlib/utils"
                            "When launched it simply gets the current structure of files and folders of the project. No arguments needed.")
        default_config = {}
        tool_args = [
                        {
                            "name": "map_root_dir",
                            "type": "string",
                            "description": "Root directory to extract the tree of files and subdirectories. Default '.'",
                            "required": True,
                        },
                    ] + environ_arg
        pm_tool = ServerTool('get_files_map', tool_name=tool_name, tool_description=tool_description, default_config=default_config, tool_args=tool_args)

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
                    ] + environ_arg
        gs_tool = ServerTool('google_search', tool_name=tool_name, tool_description=tool_description, default_config=default_config, tool_args=tool_args)

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
                    ] + environ_arg
        br_tool = ServerTool('browse_url', tool_name=tool_name, tool_description=tool_description, default_config=default_config, tool_args=tool_args)

        # VECTOR DATABASE
        tool_name = 'rag_vector_database'
        vdb_name = 'test_VDB_tmp'
        tool_description = "Tool to send queries and make retrieval augmented generation."
        default_config = {
            'vdb_mode': 'retrieval',
            'raw_sources': [],
            'seeds_chunking_threshold': 900,
            'vdb_name': vdb_name,
            'vdb_chunking_threshold': 150,
            'vdb_query': None,
            'vdb_wd': 'C:/Users/AlejandroPrendesCabo/Desktop/proyectos/swarm-automations',
            'lang': 'eng',
        }
        tool_args = [
                        {
                            "name": "vdb_query",
                            "type": "string",
                            "description": "Query to make the retrieval of relevant information. Use several search terms semantically similar to a possible answer.",
                            "required": True,
                        },
                    ] + environ_arg
        vdb_tool = ServerTool('vector_database', tool_name=tool_name, tool_description=tool_description, default_config=default_config, tool_args=tool_args)

        if use_tools:
            self.tools_dict = {
            'code_interpreter': ci_tool,
            'sources_parser_and_summarizer': sp_tool,
            'file_operations_tools': fo_tool,
            'get_files_map': pm_tool,
            'google_search': gs_tool,
            'browse_url': br_tool,
            # 'rag_vector_database': vdb_tool,
        }
        else:
            self.tools_dict = {}

        # Common attributes
        self.assistant_name = assistant_name
        self.target_project_folder = target_project_folder
        self.environments = environments
        self.address_node = address_node

        # Model configuration
        self.user_model = user_model
        self.agent_model = agent_model
        self.eval_model = eval_model
        self.user_reasoning_effort = user_reasoning_effort
        self.agent_reasoning_effort = agent_reasoning_effort
        self.eval_reasoning_effort = eval_reasoning_effort
        self.temperature = temperature

        # Runtime settings
        self.use_cloud = use_cloud
        self.use_wandb = use_wandb
        self.n_thread = n_thread
        self.use_guidance = use_guidance
        self.lang = lang

        # Tool configuration (would need to be imported from the original config)
        self.tool_choice = 'auto'

        # Dataset names
        self.seeds_dataset_name = f"{assistant_name}_SEEDS"
        self.gen_input_dataset_name = f"{assistant_name}_SEEDS"
        self.gen_output_dataset_name = f"{assistant_name}_GEN"
        self.hist_output_dataset_name = f"{assistant_name}_GEN_HIST"
        self.ft_dataset_name = f"{assistant_name}_FT"
        self.eval_input_dataset_name = f"{assistant_name}_GEN"
        self.eval_output_dataset_name = f"{assistant_name}_EVAL"
        self.eval_hist_output_dataset_name = f"{assistant_name}_HIST_EVAL"

        self.user_context = """
# CONTEXT:
You are a code examinator.
You ask simple code questions that can be solved in simple code operations lime 'Calculate the sqrt of 4 using python.'
Your first message must be a coding question. Specify to use the code executor to answer.
"""
        self.user_instructions = """
# INSTRUCTIONS:
* You simply ask questions.
* Provide clear requirements, constraints and expectations for the code you want to be written or analysed.
"""
        self.agent_context = f"""
# CONTEXT:
You are an advanced AI software developer that helps the user to work in several projects you can edit, develop, launch...
Projects: {str(self.environments)}
"""
        self.agent_instructions = ""
        self.eval_instructions = """
# INSTRUCTIONS:
Given the conversation so far, evaluate the assistant response on correctness and helpfulness (0–10).
"""

        self.tools_register = [t.get_tool_dict() for t in self.tools_dict.values()]

    def initialize(self, update=None):
        cfg = {
            'agent_model': self.agent_model,
            'user_model': self.user_model,
            'eval_model': self.eval_model,
            'user_reasoning_effort': self.user_reasoning_effort,
            'agent_reasoning_effort': self.agent_reasoning_effort,
            'eval_reasoning_effort': self.eval_reasoning_effort,
            'temperature': self.temperature,
            'tools_dict': self.tools_dict or {},
            'tool_choice': self.tool_choice,
            'use_cloud': self.use_cloud
        }
        return cfg | (update or {})

    def dataset_generation(self, raw_sources=None, seeds_chunking_threshold=900, update=None):
        cfg = {
            'raw_sources': raw_sources or [],
            'lang': self.lang,
            'seeds_dataset_name': self.seeds_dataset_name,
            'seeds_chunking_threshold': seeds_chunking_threshold,
            'use_cloud': self.use_cloud
        }
        return cfg | (update or {})

    def dataset_labeling(self, gen_static_user=False, gen_max_iter=1, gen_n_epoch=10, gen_use_agent_steering=True, del_steering=True, update=None):
        cfg = {
            'gen_input_dataset_name': self.gen_input_dataset_name,
            'gen_output_dataset_name': self.gen_output_dataset_name,
            'hist_output_dataset_name': self.hist_output_dataset_name,
            'gen_static_user': gen_static_user,
            'gen_max_iter': gen_max_iter,
            'gen_n_epoch': gen_n_epoch,
            'gen_use_agent_steering': gen_use_agent_steering,
            'del_steering': del_steering,
            'n_thread': self.n_thread,
            'use_guidance': self.use_guidance,
            'n_samples': None,
            'use_cloud': self.use_cloud,
            'use_wandb': self.use_wandb,
            # Context and instructions (would need to be defined)
            'user_context': self.user_context,
            'user_instructions': self.user_instructions,
            'agent_context': self.agent_context,
            'agent_instructions': self.agent_instructions,
            'eval_instructions': self.eval_instructions,
        }
        return cfg | (update or {})

    def train(self, perc_split=0.2, run_ft=True, n_epochs=1, ft_model='gpt-4.1-mini', update=None):
        cfg = {
            'hist_output_dataset_name': self.hist_output_dataset_name,
            'ft_dataset_name': self.ft_dataset_name,
            'perc_split': perc_split,
            'run_ft': run_ft,
            'n_epochs': n_epochs,
            'ft_model': ft_model,
            'use_cloud': self.use_cloud,
            'tools': self.tools_register
        }
        return cfg | (update or {})

    def eval(self, eval_static_user=True, eval_max_iter=1, eval_use_agent_steering=False, update=None):
        cfg = {
            'eval_input_dataset_name': self.eval_input_dataset_name,
            'eval_output_dataset_name': self.eval_output_dataset_name,
            'eval_hist_output_dataset_name': self.eval_hist_output_dataset_name,
            'eval_static_user': eval_static_user,
            'eval_max_iter': eval_max_iter,
            'eval_use_agent_steering': eval_use_agent_steering,
            'n_thread': self.n_thread,
            'n_samples': None,
            'use_cloud': self.use_cloud,
            'use_wandb': self.use_wandb,
            'hypothesis': f"Software developer assistant that can be used as a tool for developing advanced software.",
            # Context and instructions
            'user_context': self.user_context,
            'user_instructions': self.user_instructions,
            'agent_context': self.agent_context,
            'agent_instructions': self.agent_instructions,
            'eval_instructions': self.eval_instructions,
        }
        return cfg | (update or {})

    def predict(self, history=None, update=None):
        cfg = {
            'agent_context': self.agent_context,
            'agent_instructions': self.agent_instructions,
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
            'user_message': 'Suma 1 + 1 en el interpreter de eigenlib',
            'history': history or {}
        }
        return cfg | (update or {})

    def telegram_chatbot_run(self, bot_token="7775699333:AAHYOw3YsEtxgKZg1eUzUCl7lfrEQFnAH5o", update=None):
        cfg = {
            'BOT_TOKEN': bot_token,
            # Include initialization parameters
            **self.initialize()
        }
        return cfg | (update or {})

    def launch_frontend(self, update=None):
        cfg = {
            'assistant_name': self.assistant_name
        }
        return cfg | (update or {})

