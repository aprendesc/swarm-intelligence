import unittest
from eigenlib.utils.project_setup import ProjectSetupClass
ProjectSetupClass(project_folder='swarm-intelligence', test_environ=True)

"""Integration tests"""
class TestMainClass(unittest.TestCase):
    def setUp(self):
        from eigenlib.utils.testing_utils import TestingUtilsClass, test_class_code_coverage
        from swarmintelligence.main import MainClass
        ################################################################################################################
        self.test_df, self.model, self.image, self.texto = TestingUtilsClass().get_dummy_data()
        test_class_code_coverage(self, MainClass)
        self.main = MainClass({
            'hypothesis': """Test assistant.""",
            'use_cloud': False,
            'use_wandb': True,
        })

    def test_initialize(self):
        ################################################################################################################
        config = {
            'assistant_name': 'test_assistant',
            'user_model': 'gpt-4.1-mini',
            'agent_model': 'gpt-4.1-mini',
            'eval_model': 'gpt-4.1',
            'user_reasoning_effort': None,
            'agent_reasoning_effort': None,
            'eval_reasoning_effort': None,
            'temperature': 0,
            'tools_dict': {},
            'tool_choice': 'auto',
        }
        ################################################################################################################
        updated_config = self.main.initialize(config)

    def test_tools_setup(self):
        ################################################################################################################
        config = {
            'raw_sources': ['https://ai-2027.com/'],
            'lang': 'spa',
            'vdb_name': 'test_assistant_VDB',
            'vdb_chunking_threshold': 1550,
        }
        ################################################################################################################
        updated_config = self.main.tools_setup(config)

    def test_dataset_generation(self):
        ############################################################################################################
        config = {
            'raw_sources': ['https://ai-2027.com/'],
            'lang': 'spa',
            'seeds_dataset_name': 'test_dataset_SEEDS',
            'seeds_chunking_threshold': 900,
        }
        ############################################################################################################
        updated_config = self.main.dataset_generation(config)

    def test_dataset_labeling(self):
        ################################################################################################################
        config = {
            'use_cloud': False,
            'use_wandb': True,
            'n_samples': 2,
            'assistant_name': 'test_assistant',
            'user_model': 'gpt-4.1-mini',
            'agent_model': 'gpt-4.1-mini',
            'eval_model': 'gpt-4.1',
            'user_reasoning_effort': None,
            'agent_reasoning_effort': None,
            'eval_reasoning_effort': None,
            'temperature': 0,
            'tools_dict': {},
            'tool_choice': 'auto',
            'n_thread': 16,
            'use_guidance': True,
            'gen_input_dataset_name': 'test_assistant_SEEDS',
            'gen_output_dataset_name': 'test_assistant_GEN',
            'hist_output_dataset_name': 'test_assistant_GEN_HIST',
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
        }
        ################################################################################################################
        updated_config = self.main.dataset_labeling(config)

    def test_train(self):
        ################################################################################################################
        config = {
            'hist_output_dataset_name': 'test_assistant_GEN_HIST',
            'ft_dataset_name': 'test_assistant_FT',
            'perc_split': 0.2,
            'run_ft': False,
            'n_epochs': 1,
            'ft_model': 'gpt-4.1-nano',
        }
        ################################################################################################################
        updated_config = self.main.train(config)

    def test_eval(self):
        ################################################################################################################
        config = {
            'hypothesis': """Test assistant.""",
            'use_cloud': False,
            'use_wandb': True,
            'n_samples': 2,
            'assistant_name': 'test_assistant',
            'user_model': 'gpt-4.1-mini',
            'agent_model': 'gpt-4.1-mini',
            'eval_model': 'gpt-4.1',
            'user_reasoning_effort': None,
            'agent_reasoning_effort': None,
            'eval_reasoning_effort': None,
            'temperature': 0,
            'tools_dict': {},
            'tool_choice': 'auto',
            'n_thread': 16,
            'eval_input_dataset_name': 'test_assistant_GEN',
            'eval_output_dataset_name': 'test_assistant_EVAL',
            'eval_hist_output_dataset_name': 'test_assistant_HIST_EVAL',
            'eval_static_user': True,
            'eval_max_iter': 1,
            'eval_use_agent_steering': False,
            'use_guidance': True,
            'gen_input_dataset_name': 'test_assistant_SEEDS',
            'gen_output_dataset_name': 'test_assistant_GEN',
            'hist_output_dataset_name': 'test_assistant_GEN_HIST',
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
        }
        ################################################################################################################
        updated_config = self.main.eval(config)

    def test_predict(self):
        ################################################################################################################
        config = {
            'hypothesis': """Test assistant.""",
            'use_cloud': False,
            'use_wandb': True,
            'n_samples': 2,
            # INITIALIZE
            'assistant_name': 'test_assistant',
            'user_model': 'gpt-4.1-mini',
            'agent_model': 'gpt-4.1-mini',
            'eval_model': 'gpt-4.1',
            'user_reasoning_effort': None,
            'agent_reasoning_effort': None,
            'eval_reasoning_effort': None,
            'temperature': 0,
            'tools_dict': {},
            'tool_choice': 'auto',
            # SOURCES INDEXATION
            'raw_sources': ['https://ai-2027.com/'],
            'lang': 'spa',
            'seeds_dataset_name': 'test_assistant' + '_SEEDS',
            'seeds_chunking_threshold': 900,
            # TOOLS SETUP
            'vdb_name': 'test_assistant' + '_VDB',
            'vdb_chunking_threshold': 150,
            # DATASET GENERATION AND PREDICTION
            'n_thread': 16,
            'use_guidance': True,
            'gen_input_dataset_name': 'test_assistant' + '_SEEDS',
            'gen_output_dataset_name': 'test_assistant' + '_GEN',
            'hist_output_dataset_name': 'test_assistant' + '_GEN_HIST',
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
            'ft_dataset_name': 'test_assistant' + '_FT',
            'perc_split': 0.2,
            'run_ft': True,
            'n_epochs': 1,
            'ft_model': 'gpt-4.1-nano',
            # EVAL
            'eval_input_dataset_name': 'test_assistant' + '_GEN',
            'eval_output_dataset_name': 'test_assistant' + '_EVAL',
            'eval_hist_output_dataset_name': 'test_assistant' + '_HIST_EVAL',
            'eval_static_user': True,
            'eval_max_iter': 1,
            'eval_use_agent_steering': False,
            # PREDICT
            'steering': None,
            'img': 'https://www.webconsultas.com/sites/default/files/styles/wch_image_schema/public/media/0d/temas/el-caballo-pinto.jpg',
            'user_message': 'Que ves en la imagen?',

        }
        ################################################################################################################
        self.main.initialize(config)
        updated_config = self.main.predict(config)
        print(updated_config['state_dict']['answer'])

    def test_telegram_chatbot_run(self):
        import threading
        import time
        ################################################################################################################
        config = {
            'hypothesis': """Test assistant.""",
            'use_cloud': False,
            'use_wandb': True,
            'n_samples': 2,
            # INITIALIZE
            'assistant_name': 'test_assistant',
            'user_model': 'gpt-4.1-mini',
            'agent_model': 'gpt-4.1-mini',
            'eval_model': 'gpt-4.1',
            'user_reasoning_effort': None,
            'agent_reasoning_effort': None,
            'eval_reasoning_effort': None,
            'temperature': 0,
            'tools_dict': {},
            'tool_choice': 'auto',
            # SOURCES INDEXATION
            'raw_sources': ['https://ai-2027.com/'],
            'lang': 'spa',
            'seeds_dataset_name': 'test_assistant' + '_SEEDS',
            'seeds_chunking_threshold': 900,
            # TOOLS SETUP
            'vdb_name': 'test_assistant' + '_VDB',
            'vdb_chunking_threshold': 150,
            # DATASET GENERATION AND PREDICTION
            'n_thread': 16,
            'use_guidance': True,
            'gen_input_dataset_name': 'test_assistant' + '_SEEDS',
            'gen_output_dataset_name': 'test_assistant' + '_GEN',
            'hist_output_dataset_name': 'test_assistant' + '_GEN_HIST',
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
            'ft_dataset_name': 'test_assistant' + '_FT',
            'perc_split': 0.2,
            'run_ft': True,
            'n_epochs': 1,
            'ft_model': 'gpt-4.1-nano',
            # EVAL
            'eval_input_dataset_name': 'test_assistant' + '_GEN',
            'eval_output_dataset_name': 'test_assistant' + '_EVAL',
            'eval_hist_output_dataset_name': 'test_assistant' + '_HIST_EVAL',
            'eval_static_user': True,
            'eval_max_iter': 1,
            'eval_use_agent_steering': False,
            # PREDICT
            'steering': None,
            'img': 'https://www.webconsultas.com/sites/default/files/styles/wch_image_schema/public/media/0d/temas/el-caballo-pinto.jpg',
            'user_message': 'Que ves en la imagen?',

        }
        ################################################################################################################
        self.main.initialize(config)
        def aux_fun():
            updated_config = self.main.telegram_chatbot_run(config)
        bot_thread = threading.Thread(target=aux_fun, daemon=True)
        bot_thread.start()
        time.sleep(1)

    def test_launch_front(self):
        import os, tempfile, shutil, time, subprocess, types, threading
        tmp_root = tempfile.mkdtemp()
        ################################################################################################################
        os.environ['PROJECT_ROOT'] = tmp_root
        os.environ['PROJECT_NAME'] = 'demo_proj'
        os.environ['PROJECT_FOLDER'] = 'demo_proj'
        front_dir = os.path.join(tmp_root, 'demo_proj', 'modules')
        os.makedirs(front_dir, exist_ok=True)
        open(os.path.join(front_dir, 'frontend.py'), 'w').write("print('Frontend dummy')")
        ################################################################################################################
        orig_run = subprocess.run
        def _run_with_timeout(cmd, shell=True):
            proc = subprocess.Popen(cmd, shell=shell)
            time.sleep(3)  # ventana/servidor vivo 3 s
            proc.terminate()
            return types.SimpleNamespace(args=cmd, returncode=0)
        subprocess.run = _run_with_timeout
        def _worker():
            self.main.launch_front({})
        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        t.join()
        subprocess.run = orig_run
        shutil.rmtree(tmp_root)
        print("✓ launch_front probado (servidor iniciado 3 s y cerrado).")
        updated_config = self.main.launch_front({})

"""Unit tests"""
class TestModulesClass(unittest.TestCase):
    def setUp(self):
        import os
        from eigenlib.utils.testing_utils import TestingUtilsClass, module_test_coverage
        ################################################################################################################
        module_test_coverage(os.environ['PROJECT_NAME'] + '.modules', self)
        self.test_df, self.model, self.image, self.texto = TestingUtilsClass().get_dummy_data()

    def test_bash_console_tool(self):
        import types, json, subprocess
        from swarmintelligence.modules.bash_console_tool import BashConsoleInterpreterToolClass
        _subproc_original = subprocess.run
        def _fake_run(*args, **kwargs):
            return types.SimpleNamespace(returncode=0, stdout="Hello PowerShell\n", stderr="")
        subprocess.run = _fake_run
        tool = BashConsoleInterpreterToolClass(timeout_seconds=5)
        out_json = tool.run('Write-Output "Hello PowerShell"')
        print(json.loads(out_json))
        subprocess.run = _subproc_original

    def test_custom_assistant_tool(self):
        from swarmintelligence.modules.custom_assistant_tool import CustomAssistantTool
        ################################################################################################################
        config = {
            'hypothesis': """Test assistant.""",
            'use_cloud': False,
            'use_wandb': True,
            'n_samples': 2,
            # INITIALIZE
            'assistant_name': 'test_assistant',
            'user_model': 'gpt-4.1-mini',
            'agent_model': 'gpt-4.1-mini',
            'eval_model': 'gpt-4.1',
            'user_reasoning_effort': None,
            'agent_reasoning_effort': None,
            'eval_reasoning_effort': None,
            'temperature': 0,
            'tools_dict': {},
            'tool_choice': 'auto',
            # SOURCES INDEXATION
            'raw_sources': ['https://ai-2027.com/'],
            'lang': 'spa',
            'seeds_dataset_name': 'test_assistant' + '_SEEDS',
            'seeds_chunking_threshold': 900,
            # TOOLS SETUP
            'vdb_name': 'test_assistant' + '_VDB',
            'vdb_chunking_threshold': 150,
            # DATASET GENERATION AND PREDICTION
            'n_thread': 16,
            'use_guidance': True,
            'gen_input_dataset_name': 'test_assistant' + '_SEEDS',
            'gen_output_dataset_name': 'test_assistant' + '_GEN',
            'hist_output_dataset_name': 'test_assistant' + '_GEN_HIST',
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
            'ft_dataset_name': 'test_assistant' + '_FT',
            'perc_split': 0.2,
            'run_ft': True,
            'n_epochs': 1,
            'ft_model': 'gpt-4.1-nano',
            # EVAL
            'eval_input_dataset_name': 'test_assistant' + '_GEN',
            'eval_output_dataset_name': 'test_assistant' + '_EVAL',
            'eval_hist_output_dataset_name': 'test_assistant' + '_HIST_EVAL',
            'eval_static_user': True,
            'eval_max_iter': 1,
            'eval_use_agent_steering': False,
            # PREDICT
            'steering': None,
            'img': 'https://www.webconsultas.com/sites/default/files/styles/wch_image_schema/public/media/0d/temas/el-caballo-pinto.jpg',
            'user_message': 'Que ves en la imagen?',

        }
        ################################################################################################################
        tool = CustomAssistantTool(config, tool_description='dummy desc')
        tool.initialize()
        print(tool.run(query='hola'))

    def test_frontend(self):
        print('Already tested')

    def test_python_code_interpreter_tool(self):
        from swarmintelligence.modules.python_code_interpreter_tool import PythonCodeInterpreterToolClass
        print(PythonCodeInterpreterToolClass(timeout_seconds=5).run(code_str='print("Hola mundo")'))

    def test_telegram_chatbot(self):
        print('Already tested')

    def test_web_search_tool(self):
        import json
        from swarmintelligence.modules.web_search_tool import WebSearchTool
        tool = WebSearchTool()
        out = tool.run(query="openai gpt-4", num_results=3)
        print(json.loads(out))

if __name__ == '__main__':
    unittest.main()