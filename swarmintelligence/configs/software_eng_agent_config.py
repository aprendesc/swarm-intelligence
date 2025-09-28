from eigenlib.genai.environments.general_dataset_generator import EnvConfigGeneralDatasetGenerator
from swarmintelligence.modules.general_agent import GeneralAgent
from eigenlib.genai.environments.general_synth_user import GeneralSynthUser
from eigenlib.genai.tools.code_interpreter_toolbox import InterpreterTool
from eigenlib.genai.tools.web_search_toolbox import WebSearchTool
from eigenlib.genai.tools.files_browser_toolbox import FilesBrowserTool

class Config:
    def __init__(self, sample=None):
        self.project_folder = 'swarm-intelligence'
        self.agent_name = 'software_engineer_assistant'
        self.environments = ["swarmintelligence", 'eigenlib']
        self.memory_file = './data/raw/agent_memory/' + self.project_folder + '/memory.pkl'
        self.interface = {
            'parametro_1': 'Test_param',
        }

        # AGENT
        ci_tool = InterpreterTool(python_executable="python", shell_executable="/bin/bash")
        sp_tool = WebSearchTool(default_max_results=5, default_region="wt-wt")
        fb_tool = FilesBrowserTool()

        tools_dict = [ci_tool, sp_tool, fb_tool]

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

