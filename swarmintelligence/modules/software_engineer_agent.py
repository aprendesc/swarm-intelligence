import json
from pathlib import Path
import os
from eigenlib.genai.llm_client import LLMClient
from swarmintelligence.modules.code_interpreter_toolbox import InterpreterToolbox
from swarmintelligence.modules.files_browser_toolbox import FilesBrowserToolbox
from eigenlib.genai.memory import Memory
from swarmintelligence.modules.memory_manager import MemoryManager

class SoftwareEngineerAgent:
    def __init__(self, project_folder='swarm-intelligence'):
        # CONFIGURATION
        self.id = 'SOFTWARE_ENGINEER_AGENT'
        self.project_folder = project_folder
        self.memory_file = f'./data/raw/{self.id}_agent_memory.pkl'
        self.model = 'o3'
        self.client = 'oai_2'
        self.temperature = 1
        self.tool_choice = 'auto'
        self.reasoning_effort = 'high'
        self.use_steering = False
        self.memory_threshold = 10000

        # UTILS
        self.mm = MemoryManager()

        # TOOLS
        executable = 'C:/Users/AlejandroPrendesCabo/Desktop/proyectos/swarm-intelligence/.venv/Scripts/python.exe'
        bash_executable = 'C:/Program Files/Git/bin/bash.exe'
        ci_tool = InterpreterToolbox(python_executable=executable, shell_executable=bash_executable)
        fb_tool = FilesBrowserToolbox()
        self.toolboxes = [ci_tool, fb_tool]

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
        DIRECTORIOS_EXCLUIDOS = {".venv", "__pycache__", ".git", "build", "dist"}
        EXTENSIONES_EXCLUIDAS = {".jpg", ".jpeg", ".png", ".gif", ".pkl"}
        archivos_py_project = list(self.buscar_archivos(".", "*", dirs_excluidos=DIRECTORIOS_EXCLUIDOS, exts_excluidas=EXTENSIONES_EXCLUIDAS))
        archivos_py_eigen = list(self.buscar_archivos("../eigenlib", "*", dirs_excluidos=DIRECTORIOS_EXCLUIDOS, exts_excluidas=EXTENSIONES_EXCLUIDAS))

        system_prompt = f"""
# CONTEXTO:
Actua como un desarrollador de software experto, capaz de operar una serie de herramientas que te permiten desarrollar software de forma autónoma en el contexto de proyectos de Python. 

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
    
## ESTRUCTURA DE LOS PROYECTOS
### RUTAS:
'.' -> Raiz del proyecto
'../eigenlib' -> Raiz de la librería eigenlib.

### ARCHIVOS Y CARPETAS DE {self.project_folder}
{archivos_py_project}

### ARCHIVOS Y CARPETAS DE eigenlib
{archivos_py_eigen}

## METODOLOGÍA DE DESARROLLO
Dispones de herramientas que te permiten desarrollar dentro de un proyecto específico. 
Cada proyecto tiene su propio intérprete que deberás seleccionar ya que eres capaz de desarrollar o trabajar sobre el código de diferentes proyectos simultáneamente. 

El pipeline de desarrollo es:
"""
        return system_prompt

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = SoftwareEngineerAgent()
    memory = agent.initialize()
    memory, answer = agent.call(memory=memory, user_message='Ejecuta factorial de 10 en consola de python.')
    memory, answer = agent.call(memory=memory, user_message='Que modulos tengo en la carpeta modulos del proyecto eigenlib?')
    memory, answer = agent.call(memory=memory, user_message='Ejecuta un "hola mundo" en la consola bash a modo de prueba')
