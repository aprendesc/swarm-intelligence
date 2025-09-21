from datetime import date

class Config:
    def __init__(self, version='v5', sample=None):
        # TOOL SETUP
        from eigenlib.utils.notion_io import NotionIO
        from swarmintelligence.modules.notion_tool import NotionTool
        notion_token = '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'
        database_id = "2262a599-e985-8017-9faf-dd11b3b8df8b"
        notion_tool = NotionTool(auth_token=notion_token, database_id=database_id)
        tools_dict = [notion_tool]

        database_df = NotionIO(auth_token=notion_token).get_database_pages(database_id=database_id)
        active_projects = list(set(database_df['Project'].sum()))

        system_prompt = f"""
# CONTEXTO:
Eres un asistente cuya misión es la de gestionar mi notion personal.
Tienes la capacidad de realizar las operaciones necesarias para gestionar mis tareas y proyectos usando la herramienta 'notion_tool'.

# ESTRUCTURA TIPICA DE UN PROYECTO

Las paginas se organizan con atributos que son:
    * Project -> Proyecto al que petenece la pagina/epica # {active_projects}
    * Status -> Estado de la epica. ['Active', 'Fixed', 'Stand By', 'Done']
    * Target Date -> Fecha en la que se propone el cierre de la tarea. Por defecto se pone la fecha de hoy. {date.today().strftime("%Y-%m-%d")}

## PAGINAS FIJADAS O FIXED:
Toda mi organización se encuentra estructurada en una base de datos donde cada pagina es una epica (conjunto de tareas).
Las epicas fixed son epicas continuas que contienen información de descripción del proyecto.
En concreto hay una epica fixed en cada proyecto con información de:
    * Stakeholders
    * Descripción y objetivos del proyecto.
    * Notas y documentación adicional.
    
Siempre que necesites entender un proyecto o te falte información de contexto puedes acudir a estas páginas. Tambien me ayudaras a ampliarlas y detallarlas cuando te lo pida.

## PAGINAS ACTIVAS:
Las épicas o paginas Active son las tareas activas en ejecución.
Cada pagina se corresponde con una épica y debe estar redactada en formato markdown con una estructura como:

# Header
## Descripcion
Descripcion de la epica.
## Tareas
* Tarea 1
* Tarea 2
## Notas

## PAGINAS STANDBY y DONE
La páginas standby se mantienen a la espera de ser activadas. Puedes cambiarles el estado con el metodo correspondiente de la tool.
La páginas done estan archivadas y completadas.

## ESTRATEGIA
Sirvete del metodo get_database_pages para visualizar siempre el estado de mis tareas y proyectos antes de realizar operaciones.
Si es necesario, ejecuta este metodo siempre primero para tener un overview del estado.


"""

        # AGENT
        from swarmintelligence.modules.general_agent import GeneralAgent
        self.agent = GeneralAgent(system_prompt=system_prompt, model='o3', temperature=1, tools=tools_dict)


        if True:
            # DATASET
            from swarmintelligence.modules.general_dataset_generator import EnvConfigGeneralDatasetGenerator
            self.gen = EnvConfigGeneralDatasetGenerator()
            self.dataset_size = 3

            # LABELING
            from swarmintelligence.modules.general_synth_user import GeneralSynthUser
            self.user = GeneralSynthUser()
            self.env_config_dataset = './data/processed/notion_assistant_dataset'
            self.env_config_train_dataset = './data/processed/notion_assistant_train_dataset'
            self.env_config_train_history = './data/processed/notion_assistant_train_history'
            self.env_config_test_dataset = './data/processed/notion_assistant_test_dataset'
            self.env_config_test_history = './data/processed/notion_assistant_test_history'

            #FINE TUNING
            self.ft_dataset = './data/processed/ft_dataset'
            self.ft_model = 'gpt-4.1'
            self.tools_register = ''
            self.channel = 'NOTION_AGENT'

            # GENERAL
            self.version = version
            self.sample = sample
            self.experiment_id = 'swarmintelligence'

    def initialize(self, update=None):
        cfg = {
            'agent': self.agent,
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
            'user_message': 'buenas, porfa creame con la herramienta una tarea en el proyecto jedi para recordar que debo contar hasta 10 usando falanges de dedos y metele las instrucciones dentro de como hacerlo en la pagina',
            'history': [],
        }
        return cfg | (update or {})

    def launch_frontend(self, update=None):
        cfg = {'channels': ['COST_BREAKDOWN_AGENT']}
        return cfg | (update or {})

    def telegram_chatbot_run(self, update=None):
        cfg = {}
        return cfg | (update or {})

