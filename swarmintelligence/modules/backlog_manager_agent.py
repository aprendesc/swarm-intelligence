import os
import json
from pathlib import Path
from eigenlib.genai.llm_client import LLMClient
from swarmintelligence.modules.code_interpreter_toolbox import InterpreterToolbox
from swarmintelligence.modules.web_search_toolbox import WebSearchToolbox
from swarmintelligence.modules.files_browser_toolbox import FilesBrowserToolbox
from swarmintelligence.modules.notion_toolbox import NotionToolbox
from eigenlib.genai.memory import Memory
from swarmintelligence.modules.memory_manager import MemoryManager
from eigenlib.utils.notion_io import NotionIO
from datetime import datetime

class BacklogManagerAgent:
    def __init__(self, project_folder='swarm-intelligence'):
        # CONFIGURATION
        self.id = 'NOTION_AGENT'
        self.project_folder = project_folder
        self.database_id = "2262a599-e985-8017-9faf-dd11b3b8df8b"
        self.memory_file = f'./data/raw/{self.id}_agent_memory.pkl'
        self.model = 'o4-mini'
        self.client = 'oai_1'
        self.temperature = 1
        self.tool_choice = 'auto'
        self.reasoning_effort = 'medium'
        self.memory_threshold = 10000

        # UTILS
        self.mm = MemoryManager()
        self.notion_utils = NotionIO()

        # TOOLS
        ci_tool = InterpreterToolbox(python_executable='C:/Users/AlejandroPrendesCabo/Desktop/proyectos/swarm-intelligence/.venv/Scripts/python.exe', shell_executable='C:/Program Files/Git/bin/bash.exe')
        sp_tool = WebSearchToolbox(default_max_results=5, default_region="wt-wt")
        fb_tool = FilesBrowserToolbox()
        n_tool = NotionToolbox(ALLOWED_PROJECTS=['swarm-intelligence', 'eigenlib'])
        self.toolboxes = [ci_tool, sp_tool, fb_tool, n_tool]

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
        db_df = self.notion_utils.get_database_pages(self.database_id)
        db_df = db_df[db_df['status'].apply(lambda x: x in ['Fixed', 'Active', 'Stand By'])]
        db_df = db_df[['id', 'target_date', 'project', 'category', 'status', 'name']]
        system_prompt = f"""
# CONTEXTO:
Actua como un backlog manager de un notion experto en operar con la estructura de paginas de tareas.
Tu función principal es ayudarme a organizar, registrar y mantener al día toda mi información en Notion.
Dispones de una herramienta que te permite crear, leer, actualizar y borrar páginas dentro de mis bases de datos de Notion.
Para tu información, la fecha actual es: {now} 

# INSTRUCCIONESTu objetivo es operar mi database personal de sesiones de trabajo.
Cada sesión de trabajo va asociada a un proyecto y contiene en su interior una o varias tareas a realizar.Una sesión de trabajo es el equivalente a una épica de las metodologías agile.
Cada sesión de trabajo tiene asociada una fecha de deadline y un status segun si esta:
* Active: Sesiones de trabajo activas, en curso, tienen una fecha asignada.
* Fixed: Son sesiones o bloques de información pineados porque son relevantes a lo largo de todo el tiempo.
* Stand By: Son sesiones de trabajo que en algún momento se deben poner activas, no es necesario que tengan fecha.
* Closed: Sesiones de trabajo cerradasCuando te solicite información de proyectos y tareas debes abrir las correspondientes paginas de tarea, leer su resultado y responder a mis cuestiones.

Tambien debes velar por la calidad de las páginas y el contenido en su interior.

# ESTADO DE TAREAS ACTIVE FIXED Y STANDBY{db_df.to_string()}

"""
        return system_prompt

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = BacklogManagerAgent()
    memory = agent.initialize()
    memory, answer = agent.call(memory=memory, user_message='Qué proyectos tengo activos?')
    memory, answer = agent.call(memory=memory, user_message='Cual es la tarea mas inminente?')
