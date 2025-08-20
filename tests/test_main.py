from swarmintelligence.main import MainClass
from swarmintelligence.configs.personal_assistant_config import config
import unittest

class TestMainClass(unittest.TestCase):
    def setUp(self):
        self.test_time = 100
        self.main = MainClass(config)

    def test_initialize(self):
        updated_config = self.main.initialize(config)

    def test_dataset_generation(self):
        updated_config = self.main.dataset_generation(config)

    def test_dataset_labeling(self):
        updated_config = self.main.dataset_labeling(config)

    def test_train(self):
        updated_config = self.main.train(config)

    def test_eval(self):
        updated_config = self.main.eval(config)

    def test_predict(self):
        self.main.initialize(config)
        config['user_message'] = 'hazme un rag sobre la qkv del tranformer.'
        updated_config = self.main.predict(config)
        config['user_message'] = 'Lets work on improving fine tuning of models. First of all, identify in eigenlib the file llm_client'
        updated_config = self.main.predict(config)
        print(updated_config['state_dict']['answer'])
        config['user_message'] = 'Run a basic hola mundo code and give me the answer'
        updated_config = self.main.predict(config)
        print(updated_config['state_dict']['answer'])
        config['user_message'] = 'Search in the internet the F22 raptor twr'
        updated_config = self.main.predict(config)
        print(updated_config['state_dict']['answer'])

    def test_telegram_chatbot_run(self):
        import threading
        import time
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
        self.main.initialize(config)
        def aux_fun():
            updated_config = self.main.telegram_chatbot_run(config)
        bot_thread = threading.Thread(target=aux_fun, daemon=True)
        bot_thread.start()
        time.sleep(self.test_time)

    def test_launch_frontend(self):
        import threading
        import time
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
        self.main.initialize(config)
        def aux_fun():
            updated_config = self.main.launch_frontend(config)
        bot_thread = threading.Thread(target=aux_fun, daemon=True)
        bot_thread.start()
        time.sleep(30000)
