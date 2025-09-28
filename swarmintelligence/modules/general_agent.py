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

class SwarmIntelligenceAgent:
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
        DIRECTORIOS_EXCLUIDOS = {".venv", "__pycache__", ".git", "build", "dist"}
        EXTENSIONES_EXCLUIDAS = {".jpg", ".jpeg", ".png", ".gif", ".pkl"}
        archivos_py_swarm = list(buscar_archivos(".", "*", dirs_excluidos=DIRECTORIOS_EXCLUIDOS, exts_excluidas=EXTENSIONES_EXCLUIDAS))
        archivos_py_eigen = list(buscar_archivos("../eigenlib", "*", dirs_excluidos=DIRECTORIOS_EXCLUIDOS, exts_excluidas=EXTENSIONES_EXCLUIDAS))
        self.system_prompt = f"""
# CONTEXTO:
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

## METODOLOGÍA DE DESARROLLO
Dispones de herramientas que te permiten desarrollar dentro de un proyecto específico. 
Cada proyecto tiene su propio intérprete que deberás seleccionar ya que eres capaz de desarrollar o trabajar sobre el código de diferentes proyectos simultáneamente. 

El pipeline de desarrollo es:

Petición -> Escritura de un código -> Ejecución de prueba -> Identificacion de posibles errores -> Debug -> Entrega del resultado validado.
Siempre que desarrolles un modulo nuevo experimental, metelo en development.
Siempre que necesites desarrollar codigo que usa modulos externos, abrelos (en la carpeta modules o en el proyecto al que pertenecen) y analiza su contenido para poder desarrollar bien las nuevas features.
        """

        self.memory_file = './data/raw/si_agent_memory.pkl'
        self.model = 'o3'
        self.client = 'oai_2'
        self.temperature = 1
        self.tool_choice = 'auto'
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
            answer = self.LLM.run(self.mm.get(memory.history, user_message, self.id), model=self.model, temperature=self.temperature, tools_config=self.tools_config, response_format=None, tool_choice=self.tool_choice)
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
    agent = SwarmIntelligenceAgent()
    memory = agent.initialize()

    # memory, answer = agent.call(memory=memory, user_message='Lista todos los archivos y carpetas del directorio actual.')
    # memory, answer = agent.call(memory=memory, user_message='Busca recursivamente todos los archivos Python (.py) en el directorio actual, excluyendo las carpetas .venv, __pycache__ y .git.')
    # memory, answer = agent.call(memory=memory, user_message='Lista solo los archivos .py del directorio actual, sin incluir subcarpetas.')
    # memory, answer = agent.call(memory=memory, user_message='Busca todos los archivos de configuración (*.json, *.yaml, *.yml) en el proyecto, excluyendo carpetas de build.')
    # memory, answer = agent.call(memory=memory, user_message='Busca todos los archivos que empiecen por "test" en el directorio actual.')
    # memory, answer = agent.call(memory=memory, user_message='Encuentra todos los archivos .txt en cualquier subdirectorio usando el patrón **/*.txt.')
    # memory, answer = agent.call(memory=memory, user_message='Busca archivos que contengan "config" en su nombre en la carpeta src.')
    # memory, answer = agent.call(memory=memory, user_message='Lee el contenido del archivo README.md.')
    # memory, answer = agent.call(memory=memory, user_message='Muestra el contenido del archivo package.json con codificación utf-8.')
    # memory, answer = agent.call(memory=memory, user_message='Lee el archivo main.py y muestra cuántas líneas tiene.')
    # memory, answer = agent.call(memory=memory, user_message='Abre el archivo de configuración config.ini y lee su contenido.')
    # memory, answer = agent.call(memory=memory, user_message='Crea un archivo llamado "test.py" con un script básico de "Hola Mundo".')
    # memory, answer = agent.call(memory=memory, user_message='Escribe un archivo requirements.txt con las dependencias: requests, pandas, numpy.')
    # memory, answer = agent.call(memory=memory, user_message='''Crea un archivo "ejemplo.json" con la siguiente estructura:
    # {
    #   "nombre": "Proyecto Test",
    #   "version": "1.0.0",
    #   "dependencias": ["flask", "sqlalchemy"]
    # }''')
    # memory, answer = agent.call(memory=memory, user_message='Genera un archivo .gitignore con las exclusiones típicas de Python: __pycache__, .venv, *.pyc.')
    # memory, answer = agent.call(memory=memory, user_message='Crea un archivo de configuración config.py con variables de entorno básicas.')
    # memory, answer = agent.call(memory=memory, user_message='En el archivo test.py, reemplaza la línea "x = 42" por "x = 100".')
    # memory, answer = agent.call(memory=memory, user_message='Modifica el archivo config.py cambiando la línea DEBUG = False por DEBUG = True.')
    # memory, answer = agent.call(memory=memory, user_message='En requirements.txt, actualiza la línea "pandas==1.0.0" por "pandas==2.0.0".')
    # memory, answer = agent.call(memory=memory, user_message='Cambia en main.py la línea de importación "from flask import Flask" por "from flask import Flask, request".')
    # memory, answer = agent.call(memory=memory, user_message='Elimina el archivo test_temp.py.')
    # memory, answer = agent.call(memory=memory, user_message='Borra el archivo backup.txt que ya no necesito.')
    # memory, answer = agent.call(memory=memory, user_message='Elimina el directorio vacío "temp" del proyecto.')
    # memory, answer = agent.call(memory=memory, user_message='Elimina completamente la carpeta "build" y todo su contenido.')
    # memory, answer = agent.call(memory=memory, user_message='Borra recursivamente el directorio "node_modules" para limpiar el proyecto.')
    # memory, answer = agent.call(memory=memory, user_message='Elimina la carpeta "tests_old" con todos sus archivos y subdirectorios.')
    # memory, answer = agent.call(memory=memory, user_message='Busca todos los archivos Python en el proyecto, lee el primero que encuentres y muestra sus primeras 10 líneas.')
    # memory, answer = agent.call(memory=memory, user_message='Explora la carpeta "docs", encuentra archivos .md, lee el README.md y luego crea una copia llamada README_backup.md.')
    # memory, answer = agent.call(memory=memory, user_message='Lista todos los archivos de configuración (.json, .yaml, .ini), lee el primero, y crea un backup con timestamp.')
    # memory, answer = agent.call(memory=memory, user_message='Busca archivos .log antiguos en el proyecto y elimínalos para limpiar espacio.')
    # memory, answer = agent.call(memory=memory, user_message='Analiza la estructura del proyecto: lista todos los .py recursivamente, cuenta líneas de código y muestra un resumen.')
    # memory, answer = agent.call(memory=memory, user_message='Crea una estructura básica de proyecto Python: carpetas src/, tests/, docs/ y archivos __init__.py.')
    # memory, answer = agent.call(memory=memory, user_message='Encuentra todos los archivos TODO.txt o similares en el proyecto y lee su contenido.')
    # memory, answer = agent.call(memory=memory, user_message='Busca archivos de configuración dispersos (.env, config.*, settings.*) y consolídalos en una carpeta config/.')
    # memory, answer = agent.call(memory=memory, user_message='Limpia el proyecto: elimina carpetas __pycache__, .pytest_cache y archivos .pyc.')
    # memory, answer = agent.call(memory=memory, user_message='Encuentra y elimina archivos temporales (*.tmp, *.temp, *~) en todo el proyecto.')
    # memory, answer = agent.call(memory=memory, user_message='Busca archivos duplicados con nombres como file.txt, file(1).txt, file_copy.txt y elimina las copias.')
    # memory, answer = agent.call(memory=memory, user_message='Genera un reporte de la estructura del proyecto: tipos de archivos, tamaños y distribución por carpetas.')
    # memory, answer = agent.call(memory=memory, user_message='Analiza todos los archivos Python del proyecto y crea un reporte con el número total de líneas de código.')
    # memory, answer = agent.call(memory=memory, user_message='Encuentra los 5 archivos más grandes del proyecto y muestra sus tamaños.')
    # memory, answer = agent.call(memory=memory, user_message='Intenta leer un archivo que no existe: archivo_inexistente.txt.')
    # memory, answer = agent.call(memory=memory, user_message='Intenta eliminar un directorio que no está vacío sin usar la opción recursiva.')
    # memory, answer = agent.call(memory=memory, user_message='Busca archivos en una ruta que no existe: /ruta/inexistente/')
    # memory, answer = agent.call(memory=memory, user_message='Intenta escribir un archivo en una ruta con permisos restringidos.')
    # memory, answer = agent.call(memory=memory, user_message='Busca todos los archivos requirements*.txt en el proyecto y lee sus dependencias.')
    # memory, answer = agent.call(memory=memory, user_message='Encuentra archivos de Docker (Dockerfile, docker-compose.*) y muestra su contenido.')
    # memory, answer = agent.call(memory=memory, user_message='Localiza archivos de configuración de CI/CD (.github/, .gitlab-ci.yml, etc.) y examina su estructura.')
    # memory, answer = agent.call(memory=memory, user_message='Busca scripts de automatización (.sh, .bat, Makefile) y lista su contenido.')
    # memory, answer = agent.call(memory=memory, user_message='Crea una copia de respaldo de todos los archivos .py en una carpeta backup_code/.')
    # memory, answer = agent.call(memory=memory, user_message='Encuentra archivos de configuración críticos y créales backup con timestamp.')
    # memory, answer = agent.call(memory=memory, user_message='Migra todos los archivos .txt de la carpeta old/ a docs/ y elimina la carpeta old/.')
    # memory, answer = agent.call(memory=memory, user_message='Ejecuta factorial de 10 en consola de python.')
    # memory, answer = agent.call(memory=memory, user_message='Crea una tarea activa en swarm intelligence que se llame "test_task"')
    memory, answer = agent.call(memory=memory, user_message='Busca en internet la pagina de wikipedia del F22 y dime cuanto empuje tienen sus motores.')
    #memory, answer = agent.call(memory=memory, user_message='Que modulos tengo en la carpeta modulos del proyecto eigenlib?')
    #memory, answer = agent.call(memory=memory, user_message='Ejecuta un "hola mundo" en la consola bash a modo de prueba')
