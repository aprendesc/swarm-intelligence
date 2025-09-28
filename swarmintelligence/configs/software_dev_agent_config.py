from eigenlib.genai.environments.general_dataset_generator import EnvConfigGeneralDatasetGenerator
from swarmintelligence.modules.general_agent import GeneralAgent
from eigenlib.genai.environments.general_synth_user import GeneralSynthUser
from swarmintelligence.modules.server_tool import ServerTool

class Config:
    def __init__(self, project_folder='swarm-intelligence', sample=None):
        self.project_folder = project_folder
        environments = [
                    "jedipoc",
                    "swarmintelligence",
                    "swarmautomations",
                    'swarmml',
                    'swarmcompute',
                    'eigenlib'
                        ]
        self.memory_file = './data/raw/agent_memory/' + self.project_folder + '/memory_1.pkl'
        self.agent_name = 'software_engineer_assistant'
        self.interface = {
            'parametro_1': 'Test_param',
        }

        # AGENT
        """Tools Setup"""
        if True:
            # CODE INTERPRETER TOOL SETUP
            environ_arg = [{
                "name": "selected_project",
                "type": "string",
                "description": "This argument allows to select the project to work with. Must be specified by user.",
                "enum": environments,
                "required": True,
            }]
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
            tool_name = 'web_search'
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
            ws_tool = ServerTool('web_search', tool_name=tool_name, tool_description=tool_description, default_config=default_config, tool_args=tool_args)

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
                            # {
                            #     "name": "query",
                            #     "type": "string",
                            #     "description": "Original user query (used only when summarising).",
                            #     "required": False,
                            # },
                            # {
                            #     "name": "summarize_search",
                            #     "type": "boolean",
                            #     "description": "True to summarise the browsed content. Default False.",
                            #     "required": False,
                            # },
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

            tools_dict = [ci_tool, sp_tool, fo_tool, pm_tool, ws_tool, br_tool]

        system_prompt = f"""
# CONTEXTO:
Eres un desarrollador de software experto, capaz de operar una serie de herramientas que te permiten desarrollar software de forma autónoma en el contexto de proyectos de Python. 

## ESTRUCTURA DE LOS PROYECTOS
Los proyectos se estructuran siempre con un arquetipo predefinido que te ayudará a trabajar sobre ellos accediendo a los archivos necesarios para avanzar en el desarrollo de las funcionalidades solicitadas. 
A continuación, se detalla la estructura del proyecto {self.project_folder} a modo de ejemplo. Todos los proyectos cuentan con una estructura equivalente. 

{self.project_folder}/               ← Nivel raíz del proyecto
│
├── data/                         ← Conjunto de datos usados por la librería
│   ├── raw                       ← Almacenamiento de fuentes brutas.
│   ├── curated                   ← Almacenamiento de fuentes curadas.
│   └── processed                 ← Almacenamiento de fuentes procesadas, se usa como almacenamiento por defecto.
│
├── models/                       ← Modelos entrenados o en desarrollo
│
├── img/                          ← Imágenes de referencia, diagramas, plots
│
├── doc/                          ← Documentación del proyecto
│
├── .gitignore                    ← Exclusiones para control de versiones
│
├── requirements.txt              ← Dependencias de Python
│
└── swarmintelligence/           ← Módulo principal de la librería, generalmente mismo nombre que la carpeta principal pero sin guiones.
    │
    ├── configs/                  ← Configuraciones de ejecución
    │   ├── example_config.py
    │   ├── example2_config.py
    │   └── ...                   ← Otros *_config.py
    │
    ├── Modules/                  ← Módulos principales de la librería
    │   ├── example_module.py
    │   └── ...                   ← Otros métodos y clases
    │
    ├── Development/              ← Código auxiliar en desarrollo
    │   ├── dev_v0.py
    │   └── ...
    │
    └── main.py                   ← Punto de entrada principal
    

## METODOLOGÍA DE DESARROLLO
Dispones de herramientas que te permiten desarrollar dentro de un proyecto específico. 
Cada proyecto tiene su propio intérprete que deberás seleccionar ya que eres capaz de desarrollar o trabajar sobre el código de diferentes proyectos simultáneamente. 

El pipeline de desarrollo es:

Petición -> Escritura de un código -> Ejecución de prueba -> Identificacion de posibles errores -> Debug -> Entrega del resultado validado.
Siempre que desarrolles un modulo nuevo experimental, metelo en development.
Siempre que necesites desarrollar codigo que usa modulos externos, abrelos (en la carpeta modules o en el proyecto al que pertenecen) y analiza su contenido para poder desarrollar bien las nuevas features.
        """
        self.agent = GeneralAgent(system_prompt=system_prompt, model='o3', temperature=1, tools=tools_dict)

        # DATASET
        self.gen = EnvConfigGeneralDatasetGenerator()
        self.dataset_size = 3

        # LABELING
        self.user = GeneralSynthUser()
        self.env_config_dataset = f'./data/processed/{self.project_folder}_dataset'
        self.env_config_train_dataset = f'./data/processed/{self.project_folder}_train_dataset'
        self.env_config_train_history = f'./data/processed/{self.project_folder}_train_history'
        self.env_config_test_dataset = f'./data/processed/{self.project_folder}_test_dataset'
        self.env_config_test_history = f'./data/processed/{self.project_folder}_test_history'

        #FINE TUNING
        self.ft_dataset = './data/processed/ft_dataset'
        self.ft_model = 'o4-mini'
        self.tools_register = ''
        self.channel = 'PERSONAL_AGENT'

        # GENERAL
        self.sample = sample
        self.experiment_id = self.agent_name

    def initialize(self, update=None):
        cfg = {
            'agent': self.agent,
            'memory_file': self.memory_file,
        }
        return cfg | (update or {})

    def dataset_generation(self, update=None):
        cfg = {
            'gen': self.gen,
            'dataset_size': self.dataset_size,
            'output_dataset_path': self.env_config_dataset,
        }
        return cfg | (update or {})

    def validation_split(self, update=None):
        cfg = {
            'env_config_dataset': self.env_config_dataset,
            'perc_split': 0.2,
            'env_config_train_dataset': self.env_config_train_dataset,
            'env_config_test_dataset': self.env_config_test_dataset,
        }
        return cfg | (update or {})

    def train_evaluation(self, update=None):
        cfg = {
            'experiment_id': self.experiment_id,
            'env_config_input_train_dataset': self.env_config_train_dataset,
            'env_config_input_train_history': self.env_config_train_history,
            'env_config_input_test_dataset': self.env_config_test_dataset,
            'env_config_input_test_history': self.env_config_test_history,
            'user': self.user,
            'agent': self.agent,
            'env_config_output_train_dataset': self.env_config_train_dataset,
            'env_config_output_train_history': self.env_config_train_history,
            'env_config_output_test_dataset': self.env_config_test_dataset,
            'env_config_output_test_history': self.env_config_test_history,
            'run_train_inference': True,
            'run_val_inference': True,
        }
        return cfg | (update or {})

    def train(self, update=None):
        cfg = {
            'env_config_train_history': self.env_config_train_history,
            'env_config_test_history': self.env_config_test_history,
            'ft_dataset_name': self.ft_dataset,
            'perc_split': 0.2,
            'run_ft': True,
            'n_epochs': 2,
            'ft_model': self.ft_model,
            'tools': self.tools_register,
            'channel': self.channel,

        }
        return cfg | (update or {})

    def test_evaluation(self, update=None):
        cfg = {
            'experiment_id': self.experiment_id,
            'env_config_input_train_dataset': self.env_config_train_dataset,
            'env_config_input_train_history': self.env_config_train_history,
            'env_config_input_test_dataset': self.env_config_test_dataset,
            'env_config_input_test_history': self.env_config_test_history,
            'user': self.user,
            'agent': self.agent,
            'env_config_output_train_dataset': self.env_config_train_dataset,
            'env_config_output_train_history': self.env_config_train_history,
            'env_config_output_test_dataset': self.env_config_test_dataset,
            'env_config_output_test_history': self.env_config_test_history,
            'run_train_inference': False,
            'run_val_inference': True,
        }
        return cfg | (update or {})

    def predict(self, update=None):
        cfg = {
            'user_message': 'Busca en google sobre el F22 en el proyecto swarmintelligence y abrelo en browser para extraer la relacion empuje peso.',
            'history': [],
        }
        return cfg | (update or {})

    def launch_frontend(self, update=None):
        cfg = {'channels': ['GENERAL_AGENT']}
        return cfg | (update or {})

