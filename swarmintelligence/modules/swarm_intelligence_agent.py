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

class Agent:
    def __init__(self):
        # CONFIGURATION
        self.id = 'SI_AGENT'
        self.project_folder = 'swarm-intelligence'

        def buscar_archivos(ruta_raiz, patron="*", *, dirs_excluidos=None, exts_excluidas=None):
            """
            Generador que busca archivos recursivamente, excluyendo de forma eficiente
            los directorios y extensiones especificados.
            """
            dirs_excluidos = dirs_excluidos or set()
            exts_excluidas = exts_excluidas or set()

            for raiz, dirs, archivos in os.walk(ruta_raiz):
                # Poda el árbol de búsqueda para no entrar en directorios excluidos
                dirs[:] = [d for d in dirs if d not in dirs_excluidos]

                for nombre_archivo in archivos:
                    p = Path(raiz) / nombre_archivo
                    if p.suffix not in exts_excluidas and p.match(patron):
                        yield str(p)

        # PROMPT BUILDING
        from eigenlib.utils.notion_io import NotionIO
        from datetime import datetime
        notion = NotionIO()
        database_id = "2262a599-e985-8017-9faf-dd11b3b8df8b"
        db_df = notion.get_database_pages(database_id)
        db_df = db_df[db_df['status'].apply(lambda x: x in ['Fixed', 'Active', 'Stand By'])]
        db_df = db_df[['id', 'target_date', 'project', 'category', 'status', 'name']]
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        DIRECTORIOS_EXCLUIDOS = {".venv", "__pycache__", ".git", "build", "dist"}
        EXTENSIONES_EXCLUIDAS = {".jpg", ".jpeg", ".png", ".gif", ".pkl"}
        archivos_py_swarm = list(buscar_archivos(".", "*", dirs_excluidos=DIRECTORIOS_EXCLUIDOS, exts_excluidas=EXTENSIONES_EXCLUIDAS))
        archivos_py_eigen = list(buscar_archivos("../eigenlib", "*", dirs_excluidos=DIRECTORIOS_EXCLUIDOS, exts_excluidas=EXTENSIONES_EXCLUIDAS))
        self.system_prompt = f"""
# DESARROLLO DE SOFTWARE:
Eres un desarrollador de software experto, capaz de operar una serie de herramientas que te permiten desarrollar software de forma autónoma en el contexto de proyectos de Python. 

## ESTRUCTURA DE LOS PROYECTOS
Los proyectos se estructuran siempre con un arquetipo predefinido que te ayudará a trabajar sobre ellos accediendo a los archivos necesarios para avanzar en el desarrollo de las funcionalidades solicitadas. 
A continuación, se detalla la estructura del proyecto {self.project_folder} a modo de ejemplo. Todos los proyectos cuentan con una estructura equivalente. 

Para acceder a la raiz de archivos de {self.project_folder} la ruta es '.'
Para acceder a la raiz de archivos de eigenlib la ruta es '../eigenlib'

## ARCHIVOS EN {self.project_folder}
{archivos_py_swarm}

## ARCHIVOS EN EIGENLIB
{archivos_py_eigen}

## GESTIÓN DEL PROYECTO
Mediante las herramientas de notion debes organizar, registrar y mantener al día toda mi información en Notion.
Dispones de una herramienta que te permite crear, leer, actualizar y borrar páginas dentro de mis bases de datos de Notion.

Para tu información, la fecha actual es: {ahora} 

# INSTRUCCIONES
Tu objetivo es operar mi database personal de sesiones de trabajo.
Cada sesión de trabajo va asociada a un proyecto y contiene en su interior una o varias tareas a realizar.
Una sesión de trabajo es el equivalente a una épica de las metodologías agile.
Cada sesión de trabajo tiene asociada una fecha de deadline y un status segun si esta:
* Active: Sesiones de trabajo activas, en curso, tienen una fecha asignada.
* Fixed: Son sesiones o bloques de información pineados porque son relevantes a lo largo de todo el tiempo.
* Stand By: Son sesiones de trabajo que en algún momento se deben poner activas, no es necesario que tengan fecha.
* Closed: Sesiones de trabajo cerradas

Cuando te solicite información de proyectos y tareas debes abrir las correspondientes paginas de tarea, leer su resultado y responder a mis cuestiones.
Tambien debes velar por la calidad de las páginas y el contenido en su interior.

# ESTADO DE TAREAS ACTIVE FIXED Y STANDBY
{db_df.to_string()}

## METODOLOGÍA DE DESARROLLO
Dispones de herramientas que te permiten desarrollar dentro de un proyecto específico. 
Cada proyecto tiene su propio intérprete que deberás seleccionar ya que eres capaz de desarrollar o trabajar sobre el código de diferentes proyectos simultáneamente. 
        """

        self.memory_file = './data/raw/si_agent_memory.pkl'
        self.model = 'o3'
        self.client = 'oai_2'
        self.temperature = 1
        self.tool_choice = 'auto'
        self.reasoning_effort = 'high'
        self.use_steering = False
        self.memory_threshold = 10000
        self.mm = MemoryManager()

        # TOOLS
        executable = 'C:/Users/AlejandroPrendesCabo/Desktop/proyectos/swarm-intelligence/.venv/Scripts/python.exe'
        bash_executable = 'C:/Program Files/Git/bin/bash.exe'
        ci_tool = InterpreterToolbox(python_executable=executable, shell_executable=bash_executable)
        sp_tool = WebSearchToolbox(default_max_results=5, default_region="wt-wt")
        fb_tool = FilesBrowserToolbox()
        n_tool = NotionToolbox(auth_token=os.environ['NOTION_TOKEN'], ALLOWED_PROJECTS=['swarm-intelligence', 'eigenlib'])
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
        memory.log(role='system', modality='text', content=self.system_prompt, channel=self.id)
        return memory

    def call(self, memory=None, user_message=None, **kwargs):
        memory.log(role='system', modality='text', content=self.system_prompt, steering=True, channel=self.id)
        memory.log(role='user', modality='text', content=user_message, channel=self.id)
        while True:
            answer = self.LLM.run(self.mm.get(memory.history, user_message, self.id), model=self.model, temperature=self.temperature, reasoning_effort=self.reasoning_effort, tools_config=self.tools_config, response_format=None, tool_choice=self.tool_choice)
            if type(answer) == dict:
                print('TOOL CALL: ', str(answer)[0:1000])
                memory.log(role='assistant', modality='tool_call', content = answer, channel = self.id)
                tool_answer = self._tool_call(answer)
                memory.log(role='tool', modality='tool_result', content=tool_answer, channel=self.id)
                print('TOOL: ', tool_answer['tool_call_result'][0:1000])
                print('------------------------------------------------------------------------------------------------')
            else:
                memory.log(role='assistant', modality='text', content=answer, channel = self.id)
                break
        return memory, answer

    def _tool_call(self, query):
        call_tool_name = query['function']['name']
        call_toolbox = self.tools_map[call_tool_name]
        call_args = json.loads(query['function']['arguments'])
        tool_response = call_toolbox.call(tool_name=call_tool_name, payload=call_args)
        return {'tool_call_id': query['id'], 'tool_call_function_name': query['function']['name'], 'tool_call_result': json.dumps(tool_response)}


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    agent = Agent()
    memory = agent.initialize()
    memory, answer = agent.call(memory=memory, user_message='Ejecuta factorial de 10 en consola de python.')
    memory, answer = agent.call(memory=memory, user_message='Crea una tarea activa en swarm intelligence que se llame "test_task"')
    memory, answer = agent.call(memory=memory, user_message='Busca en internet la pagina de wikipedia del F22 y dime cuanto empuje tienen sus motores.')
    memory, answer = agent.call(memory=memory, user_message='Que modulos tengo en la carpeta modulos del proyecto eigenlib?')
    memory, answer = agent.call(memory=memory, user_message='Ejecuta un "hola mundo" en la consola bash a modo de prueba')
