
"""test_assistant"""
assistant_name = 'test_assistant'
from eigenlib.LLM.base_agent_tools import VDBToolClass
tools = {'sources_search_engine': VDBToolClass(vdb_name=assistant_name + '_VDB')}
test_config = {
    'hypothesis': """Test assistant.""",
    'use_cloud': False,
    'use_wandb': True,
    'n_samples': 2,
    # INITIALIZE
    'assistant_name': assistant_name,
    'user_model': 'gpt-4.1-mini',
    'agent_model': 'gpt-4.1-mini',
    'eval_model': 'gpt-4.1',
    'user_reasoning_effort': None,
    'agent_reasoning_effort': None,
    'eval_reasoning_effort': None,
    'temperature': 0,
    'tools_dict': tools,
    'tool_choice': 'auto',
    # SOURCES INDEXATION
    'raw_sources': ['https://ai-2027.com/'],
    'lang':'spa',
    'seeds_dataset_name': assistant_name + '_SEEDS',
    'seeds_chunking_threshold': 900,
    # TOOLS SETUP
    'vdb_name': assistant_name + '_VDB',
    'vdb_chunking_threshold': 150,
    # DATASET GENERATION AND PREDICTION
    'n_thread': 16,
    'use_guidance': True,
    'gen_input_dataset_name': assistant_name + '_SEEDS',
    'gen_output_dataset_name': assistant_name + '_GEN',
    'hist_output_dataset_name': assistant_name + '_GEN_HIST',
    'gen_static_user': False,
    'gen_max_iter': 1,
    'gen_n_epoch': 10,
    'gen_use_agent_steering': True,
    'del_steering': True,
    'history': {},
    # -----------------------
    'user_context': """
# CONTEXTO:
* Eres un agente entrevistador experto en la fuente proporcionada.
""",
    'user_instructions': """
# INSTRUCCIONES:
* Genera preguntas que toquen todos los temas que cubre la fuente de información empezando por el principio del documento y avanzando paso a paso.
* Haz tanto preguntas de cosas concretas como preguntar por asuntos amplios o generales que requieran explicaciones extensas.
* No hagas referencia al documento, actua como si fueras un experto en la materia.
* Tus mensajes deben contener unicamente preguntas o consultas directas, no añadas nada más.
* Haz una pregunta en cada turno a modo de entrevista..
""",
    # -----------------------
    'agent_context': """
# CONTEXTO:    
* Eres un asistente de conocimiento que responde de forma precisa a partir de tu conocimiento interno y de fuentes externas que se te proporcionen.
""",
    'agent_instructions': """
# INSTRUCCIONES:
* Responde a las consultas del usuario con las fuentes de información que se te proporcionen.
* Responde de forma precisa, de manera clara concisa y natural.
* Responde como un experto en la materia, sin hacer referencia a las fuentes.
""",
    # -----------------------
    'eval_instructions': """
# NUEVAS INSTRUCCIONES:
A partir de la información de tu contexto evalua tu ultima respuesta del usuario.
Puntua de 0 a 10 la calidad de su ultima respuesta evaluando:

10 = La respuesta es completamente factual y correcta de acuerdo a la fuentes que conoces y target de referencia.
0 = La respuesta contiene alucinaciones, esta gravemente desviada o no responde a las cuestiones solicitadas de ninguna manera.
""",
    # TRAIN
    'ft_dataset_name': assistant_name + '_FT',
    'perc_split': 0.2,
    'run_ft': True,
    'n_epochs': 1,
    'ft_model': 'gpt-4.1-nano',
    #EVAL
    'eval_input_dataset_name': assistant_name + '_GEN',
    'eval_output_dataset_name': assistant_name + '_EVAL',
    'eval_hist_output_dataset_name': assistant_name + '_HIST_EVAL',
    'eval_static_user': True,
    'eval_max_iter': 1,
    'eval_use_agent_steering': False,
    # PREDICT
    'steering': None,
    'img': 'https://www.webconsultas.com/sites/default/files/styles/wch_image_schema/public/media/0d/temas/el-caballo-pinto.jpg',
    'user_message': 'Que ves en la imagen?',
}
########################################################################################################################

"""test_assistant/general_purpose"""
assistant_name = 'general_purpose_assistant'
from swarmintelligence.modules.web_search_tool import WebSearchTool
tools = {'intelligent_web_search': WebSearchTool()}
update_dict = {
    'hypothesis': """General purpose assistant.""",
    # INITIALIZE
    'assistant_name': assistant_name,
    'agent_model': 'o3',
    'agent_reasoning_effort': 'high',
    'temperature': 1,
    'tools_dict': tools,
    'tool_choice': 'auto',
    #INFERENCE
    'agent_context': """""",
    'agent_instructions': "You are a very precise and obedient assistant.",
    'steering': None,
    'img': None,
    'user_message': 'Ejecuta el codigo de factorial de 12 y dime el resultado.',
}
gp_assistant_config = test_config | update_dict
########################################################################################################################

"""test_assistant/code_assistant"""
assistant_name = 'software_developer_assistant'
from swarmintelligence.modules.python_code_interpreter_tool import PythonCodeInterpreterToolClass
from swarmintelligence.modules.bash_console_tool import BashConsoleInterpreterToolClass
tools = {
    'python_code_interpreter': PythonCodeInterpreterToolClass(),
    'bash_interpreter': BashConsoleInterpreterToolClass()
}
update_dict = {
    'hypothesis': """Software developer assistant that can be used as a tool for developing advanced software.""",
    # INITIALIZE
    'assistant_name': assistant_name,
    'agent_model': 'gpt-5-mini',
    'agent_reasoning_effort': 'high',
    'temperature': 1,
    'tools_dict': tools,
    'tool_choice': 'auto',
    #INFERENCE
    'agent_context': """""",
    'agent_instructions': """# PROJECT STRUCTURE
### Metadata and General Configuration (Root Directory)
.git/ → Git version control repository.
.idea/ → IDE settings (e.g., PyCharm configurations).
.venv/ → Python virtual environment directory.
Dockerfile → Container definition for Docker-based builds.
pyproject.toml, 
requirements.txt,
MANIFEST.in → Dependency management and packaging metadata.
README.md → Project documentation
changelog.md → changelog history
.gitignore → Git ignore rules.

### Data
data/
├─ raw/ → Original/raw data sources (e.g., images, CSVs, database dumps).
├─ processed/ → Data transformed and prepared for pipelines or models.
└─ curated/ → Intermediate or final-stage outputs during data extraction or curation.

### Documentation and Images
doc/ → Diagrams, architecture designs, and extended Markdown documentation (e.g., Draw.io files).
img/ → Logos, banners, and other graphical or branding assets.

### Models
models/
├─ vosk-model-small-es… → Pre-trained models (e.g., for speech recognition).
└─ *.pkl → Custom-trained model artifacts serialized as Pickle files.

### Supporting Scripts
scripts/
encrypt_env.py → Encrypt .env configuration files for secure sharing.
installation_utils.py → Installation helpers (e.g., for dependencies or setup).
setup.py → Local packaging or deployment script.
update_repos*.sh → Shell scripts to update cloned external repositories.
WheelManager.py → Utility to manage Python wheels and local packages.

# Application Code
swarmintelligence/ → Root package of the entire application.
├─ env/ → Environment configuration files (.env, encrypted versions).
├─ automations_app/ → App focused on task automation and system-level interactions.
├─ ml_models_app/ → Foundational apps for machine learning models.
└─ personal_assistant_app/ → Conversational assistant app (e.g., chatbot or voice interface).

#### Each sub-application follows a standardized internal layout:
config.py → Centralized configuration of constants, file paths, and app settings.
main.py → Main entry point (can serve as CLI or API launcher).
test.py → Quick testing or smoke-testing script.
modules/ → Core business logic organized into modular subcomponents.

### Experiment Tracking
wandb/ → Logs, results, and artifacts of each tracked experiment or run using Weights & Biases.

""" +
                          """
# PERSONAL UTILS LIBRARY
eigenlib is a Python “Swiss-Army knife” utility library that stitches together cross-cutting helpers and higher-level wrappers for data, machine learning, LLMs, audio and images. It is organized into one top-level package (`eigenlib`) with four domain subpackages plus a broad “utils” subpackage.

---

## 1. Core Package Structure

```
eigenlib/
├─ audio/       # audio capture, TTS, STT, recording, playback
├─ image/       # CLIP embeddings, DALL·E image generation
├─ LLM/         # agents, RAG, embeddings, chains, dataset generation
├─ ML/          # ETL, feature-engineering, model wrappers, pipelines & experiments
└─ utils/       # project scaffolding, data I/O, API wrappers, cloud/store, alerts, encryption, parallelism, testing
```

---

## 2. utils/ Subpackage

- **project_setup.py**  
  Bootstrap new apps: folder templates, `.env` files, project skeletons.

- **testing_utils.py**  
  Generate dummy DataFrames/models/images for quick unit tests, checkpoint/retrieve test artifacts.

- **data_utils.py**  
  Save & load tabular datasets (CSV, Parquet, Excel), manage shards, multi-threaded I/O.

- **api_utils.py**  
  Thin FastAPI server/client wrapper for local REST endpoints.

- **tcp_utils.py**  
  Simple TCP server/client abstraction for structured message exchange.

- **alert_utils.py** / **telegram_utils.py**  
  Send alerts or messages via Telegram bot API.

- **databricks_storage_utils.py** / **azure_blob_utils.py** / **snowflake_utils.py**  
  Helpers for cloud storage (upload, download, delete) and data-warehouse operations.

- **encryption_utils.py**  
  File encryption/decryption with password-based key.

- **format_conversors.py**  
  Miscellaneous converters (e.g. DataFrame↔JSON, base64 URL encoders).

- **parallel_utils.py**  
  Run arbitrary Python functions in parallel (threads or processes).

- **youtube_utils.py**  
  Download & extract audio from YouTube URLs.

- **notion_utils.py** (stub)  
  Placeholder for Notion integration helpers.

---

## 3. audio/ Subpackage

- **audio_utils.py**  
  Record, save, load, play back audio locally.

- **OAI_TTS.py** & **chatterbox_tts.py**  
  Text-to-speech engines (OpenAI / local chatterbox).

- **oai_whisper_stt.py** & **light_speech_recognition.py**  
  Speech-to-text (OpenAI Whisper & lightweight local recognizer).

- **audio_mixer_recorder.py**  
  Simple mixer / multi-channel recorder for live audio streams.

- **keyword_trigger.py**  
  Listen for spoken keywords to trigger recordings.

---

## 4. image/ Subpackage

- **CLIP_embedding_model.py**  
  Wrap a CLIP model for image/text embeddings.

- **dalle_model.py**  
  Interface to DALL·E (or DALL·E-like) image generation API.

---

## 5. LLM/ Subpackage

- **llm_client.py**  
  OpenAI API client: query, manage conversation history, stubbed fine-tuning.

- **kaia_llm.py**  
  Alternate “Kaia” LLM client class.

- **episode.py**  
  Log conversational turns (user/assistant, modalities, metadata).

- **dataset_generator.py**  
  Automatically build Q&A datasets from a text source + LLM.

- **vector_database.py**  
  Create/save/load vector stores (chunking + embeddings).

- **rag_chain.py** / **planner_rag_chain.py**  
  Retrieval-Augmented Generation chain orchestrators.

- **parallel_chain_experiment.py**  
  Run multiple RAG experiments in parallel for benchmarking.

- **markdown_web_scrapper.py** / **pdf_to_markdown.py**  
  Scrape & convert web pages or PDFs into Markdown.

- **custom_eval.py**, **base_agent_tools.py**, **computer_use_tools.py**, **sources_parser.py**, **llm_validation_split.py**  
  Helpers for evaluation, tool-based agents, parsing, splitting datasets.

---

## 6. ML/ Subpackage

- **basic_etl.py** / **etl_raw_table.py**  
  Stub ETL pipelines for ingesting raw tabular data.

- **feature_*.py**  
  Feature engineering: encoders, scalers, selectors, date fragmentation, sequence padding.

- **general_ml_experiment.py**  
  Orchestrate hyperparameter searches, experiment tracking (Weights & Biases).

- **general_ml_pipeline.py**  
  End-to-end data→model pipeline skeleton.

- **Model wrappers:**  
  - catboost_model.py  
  - lgbm_model.py  
  - xgb_model.py  
  - keras_nn_model.py  
  - pytorn_nn_model(.py)  
  - shallow_models.py  
  - ensemble_model.py  
  - multiasset_trading_strategy.py  

- **Validation splits:**  
  - basic_validation_split.py  
  - time_series_validation_split.py  

- **Metrics & logging:**  
  - metrics_backtest.py  
  - metrics_classification_regression.py  
  - wandb_logging.py  

---

## 7. Tests

The `eigenlib/test.py` module uses `unittest` to exercise nearly every helper and class:

- Project scaffolding & dummy-data generation  
- DataUtils (save/load), AlertUtils, API and TCP servers  
- Cloud storage ops (Databricks, Azure, Snowflake) & YouTube audio download  
- Image download, conversion to data-URL  
- Parallel execution patterns  
- LLM: episodes, dataset generation, RAG chains, vector DB, web/PDF scrapers  
- audio: TTS, STT, recording, playback  
- Encryption round-trips  
- ML pipeline instantiation and experiment skeleton  

---

    """,
    'steering': """
# INSTRUCTIONS:
* You are a high skilled software developer expert in developing clean, efficient, high quality code and solutions for the user's project.
* Answer always with full solutions.
* Use any tool needed. You can use the python interpreter or the shell console to solve the user's requests and instructions.
* User can't see tool outputs, you must deliver every relevant information in your answer.
* Before taking action always plan the best steps to solve the problem, you can use the tools as many times as you need and update your plan based on the new information gathered until the goal is achieved.
""",
    'img': None,
    'user_message': 'Ejecuta el codigo de factorial de 12 y dime el resultado.',
}
code_assistant_config = test_config | update_dict
########################################################################################################################

"""test_assistant/code_assistant_2"""
assistant_name = 'software_developer_2_assistant'
tools = {}
update_dict = {
    'hypothesis': """Software developer assistant that can be used as a tool for developing advanced software.""",
    # INITIALIZE
    'assistant_name': assistant_name,
    'agent_model': 'o3',
    'agent_reasoning_effort': 'high',
    'temperature': 1,
    'tools_dict': tools,
    'tool_choice': 'auto',
    #INFERENCE
    'agent_context': """""",
    'agent_instructions': """You are an expert code developer in R&D code, where we focus on having the fastest and more effective code that solves the given task."
You must follow the instructions to write code in the R&D prototyping way:
# INSTRUCTIONS FOR R&D CODE DEVELOPING:
* You never include comments or annotations of any kind in your answers.
* Every line must include a single execution of code, avoid unnecessary line jumps and also multiple executions of code in a single line. One line of code = One python command.
* Your code must carefully follow all the user's requirements.
* Dont include type annotations, error exceptions, unnecesary prints... that adds length and is not needed for functionality-
* You are VERY focused in giving the simplest code that solves the request from the user. You can reason and think internally in terms of more complex solutions but at the end you always end up simplyfiying the code with the above rules.
* Always thin all the time you need to check step by step that all requirements from the user are met.
* All the code is designed to be launched in an inline python interpreter.
* All codes must be functional just by launching the code inside python, always include the code and the launch method already configured to test it.

Simple example of R&D coding standards, indications of style are between < and >:

import pandas as pd
from numpy import *
from my_class import MyClass

class ExampleClass():
    def __init__(self):
        pass
    
    def method_1(self, argument_1, argument_2, argument_3=None): <no line jumps despite of length of arguments>
        a = argument_2 <one line for each single python command>
        b = argument_1
        c = argument_3 if argument_3 is not None else 0 <compatify when it is not too much>
        return a, b, c 

    def method_2(self, argument_1, argument_2='test'):
        <we avoid comments.>
        my_class = MyClass()
        output = my_class.run(argument_1)
        return {'a':output, 'b':2, 'c':self._aux_method()}

    @staticmethod<one line separation between methods>
    def _aux_method():
        return 1

if __name__=='__main__': <Ready to launch code>
    ec = ExampleClass()
    output1 = ec.method_2(1,, argument_2='no_test')
    print(output1)
    output2 = ec.method_2(1, argument_2='no_test')
    print(output2)
    
""",
    'steering': None,
    'img': None,
    'user_message': 'Ejecuta el codigo de factorial de 12 y dime el resultado.',
}
code_assistant_2_config = test_config | update_dict
########################################################################################################################

"""test_assistant/project_manager_assistant"""
assistant_name = 'project_manager_assistant'
from swarmintelligence.modules.custom_assistant_tool import CustomAssistantTool
tools = {
    'software_developer_assistant': CustomAssistantTool(code_assistant_config, tool_description='This tool is a software engineer from your team as manager.'),
}
update_dict = {
    'hypothesis': """This assistant is a project manager..""",
    # INITIALIZE
    'assistant_name': assistant_name,
    'agent_model': 'o3',
    'agent_reasoning_effort': 'high',
    'temperature': 1,
    'tools_dict': tools,
    'tool_choice': 'auto',
    # INFERENCE
    'agent_context': """You are an expert software project manager assistant with the responsibilities of:
Step 1: Debate with the user to define scope, milestones, ideas, and make a plan.
Stage 2: When the contract with the user and the plan is ready, start working with the developer tools.
Stage 3: Manage the team of developers as Tools: Query the developer with tasks. Oversee their results, discuss the results...
Stage 4: Report and deliver the results to the user as an answer, delivering the resulting code, paying detailed attention to the user's requests and how he wants it etc..
    """,
    'agent_instructions': "INSTRUCTIONS: All your team is made of different AI tools that you can query when you need it. Work with your team(tools) to deliver a solution to user's needs paying attention to every need and requests and ensuring you (the team) deliver the requirements.",
    'steering': None,
    'img': None,
    'user_message': 'Quiero obtener un codigo que obtenga en ascii la figura de una montaña printeada por pantalla.',
}
project_manager_assistant = test_config | update_dict
########################################################################################################################
