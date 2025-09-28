import os
import json
from pathlib import Path
from eigenlib.genai.llm_client import LLMClient
from swarmintelligence.modules.agent_communication_toolbox import AgentCommunicationToolbox
from swarmintelligence.modules.search_agent import SearchAgent
from swarmintelligence.modules.backlog_manager_agent import BacklogManagerAgent
from swarmintelligence.modules.software_engineer_agent import SoftwareEngineerAgent
from eigenlib.genai.memory import Memory
from swarmintelligence.modules.memory_manager import MemoryManager
from eigenlib.utils.notion_io import NotionIO
from datetime import datetime

class ManagerAgent:
    def __init__(self, project_folder='swarm-intelligence'):
        # CONFIGURATION
        self.id = 'MANAGER_AGENT'
        self.project_folder = project_folder
        self.project_page = '2742a599-e985-80ba-8fba-e20c1fc51a0d'
        self.database_id = "2262a599-e985-8017-9faf-dd11b3b8df8b"
        self.memory_file = f'./data/raw/{self.id}_agent_memory.pkl'
        self.model = 'gpt-4.1'
        self.client = 'oai_1'
        self.temperature = 1
        self.tool_choice = 'auto'
        self.reasoning_effort = None
        self.use_steering = False
        self.memory_threshold = 10000

        # UTILS
        self.mm = MemoryManager()
        self.notion_utils = NotionIO()

        # TOOLS
        sa = SearchAgent()
        bm = BacklogManagerAgent()
        swe = SoftwareEngineerAgent()
        sa.initialize()
        bm.initialize()
        swe.initialize()
        sa_tool = AgentCommunicationToolbox(agent_instance=sa, agent_name="search_agent" ,description="""Herramienta para contactar con el agente de búsquedas en internet. 
Las consultas deben contener todo lujo de detalles para que el agente pueda buscar con todo el contexto.""")
        bm_tool = AgentCommunicationToolbox(agent_instance=bm, agent_name="backlog_manager_agent", description="""
Herramienta para contactar con el backlog manager para operaciones de gestión de tareas en el notion de proyectos.""")
        swe_tool = AgentCommunicationToolbox(agent_instance=swe, agent_name="software_engineer_agent", description="""
Herramienta para enviar solicitudes al software engineer experto capaz de desarrollar código.""")
        self.toolboxes = [sa_tool, bm_tool, swe_tool]

    def initialize(self, memory=Memory()):
        # TOOL INITIALIZATION
        tools_map = {}
        tools_config = []
        for tb in self.toolboxes:
            tools_dicts = tb.initialize()
            for t in tools_dicts:
                tools_map[t['function']['name']] = tb
                tools_config.append(t)
        self.tools_map = tools_map
        self.tools_config = tools_config

        # LANGUAGE MODEL INITIALIZATION
        self.LLM = LLMClient(client=self.client)
        return memory

    def call(self, memory=None, user_message=None, **kwargs):
        memory.log(role='system', modality='text', content=self.system_prompt_template(), steering=True, channel=self.id)
        memory.log(role='user', modality='text', content=user_message, channel=self.id)
        while True:
            answer = self.LLM.run(self.mm.get(memory.history, user_message, self.id), model=self.model, temperature=self.temperature, reasoning_effort=self.reasoning_effort, tools_config=self.tools_config, response_format=None, tool_choice=self.tool_choice)
            if type(answer) == dict:
                print('TOOL CALL: ', str(answer)[0:1000])
                memory.log(role='assistant', modality='tool_call', content = answer, channel = self.id)
                tool_answer, memory = self._tool_call(answer, memory)
                memory.log(role='tool', modality='tool_result', content=tool_answer, channel=self.id)
                print('TOOL: ', tool_answer['tool_call_result'][0:1000])
                print('------------------------------------------------------------------------------------------------')
            else:
                memory.log(role='assistant', modality='text', content=answer, channel = self.id)
                break
        return memory, answer

    def _tool_call(self, query, memory):
        call_tool_name = query['function']['name']
        call_toolbox = self.tools_map[call_tool_name]
        call_args = json.loads(query['function']['arguments'])
        tool_response, memory = call_toolbox.call(tool_name=call_tool_name, payload=call_args, memory=memory)
        return {'tool_call_id': query['id'], 'tool_call_function_name': query['function']['name'], 'tool_call_result': json.dumps(tool_response)}, memory

    def buscar_archivos(self, ruta_raiz, patron="*", *, dirs_excluidos=None, exts_excluidas=None):
        """
        Generador que busca archivos recursivamente, excluyendo de forma eficiente
        los directorios y extensiones especificados.
        """
        dirs_excluidos = dirs_excluidos or set()
        exts_excluidas = exts_excluidas or set()

        for raiz, dirs, archivos in os.walk(ruta_raiz):
            dirs[:] = [d for d in dirs if d not in dirs_excluidos]

            for nombre_archivo in archivos:
                p = Path(raiz) / nombre_archivo
                if p.suffix not in exts_excluidas and p.match(patron):
                    yield str(p)

    def system_prompt_template(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        project_info = self.notion_utils.read_page_as_markdown(page_id=self.project_page)
        db_df = self.notion_utils.get_database_pages(self.database_id)
        db_df = db_df[db_df['status'].apply(lambda x: x in ['Fixed', 'Active', 'Stand By'])]
        db_df = db_df[['id', 'target_date', 'project', 'category', 'status', 'name']]
        DIRECTORIOS_EXCLUIDOS = {".venv", "__pycache__", ".git", "build", "dist"}
        EXTENSIONES_EXCLUIDAS = {".jpg", ".jpeg", ".png", ".gif", ".pkl"}
        archivos_py_project = list(self.buscar_archivos(".", "*", dirs_excluidos=DIRECTORIOS_EXCLUIDOS, exts_excluidas=EXTENSIONES_EXCLUIDAS))
        archivos_py_eigen = list(self.buscar_archivos("../eigenlib", "*", dirs_excluidos=DIRECTORIOS_EXCLUIDOS, exts_excluidas=EXTENSIONES_EXCLUIDAS))
        system_prompt = f"""
# SOFTWARE MANAGER:
Actua en modo **manager de software experto**, responsable de la planificación, organización y supervisión de proyectos de desarrollo.  
Tu misión es la de coordinar al equipo de agentes de desarrollo:
* Software engineer
* Backlog Manager: Agente que gestiona el notion que usamos como backlog.
* Sources search manager

# ESTADO DE TAREAS
{db_df.to_string()}

## ESTRUCTURA DE LOS PROYECTOS
### RUTAS:
'.' -> Raiz del proyecto
'../eigenlib' -> Raiz de la librería eigenlib.

### ARCHIVOS Y CARPETAS DE {self.project_folder}
{archivos_py_project}

### ARCHIVOS Y CARPETAS DE eigenlib
{archivos_py_eigen}

# INFORMACIÓN DEL PROYECTO
{project_info}
* Hora y fecha actual: {now}

## OBJETIVO
Eres mi **IA Manager de Software**, responsable de ayudar al usuario a construir los proyectos según sus necesidades y requerimientos.
"""
        return system_prompt

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = ManagerAgent()
    memory = agent.initialize()
    memory, answer = agent.call(memory=memory, user_message='Busca en internet la pagina de wikipedia del F22 y dime cuanto empuje tienen sus motores.')
    memory, answer = agent.call(memory=memory, user_message='Quiero ejecutar factorial de 10 en el interprete de python y ver que da.')

