from swarmintelligence.main import MainClass
from swarmintelligence.configs.base_config import Config
import unittest

class TestMainClass(unittest.TestCase):
    def setUp(self):
        self.test_time = 100
        self.cfg = Config()
        self.main = MainClass()

    def test_initialize(self):
        updated_config = self.main.initialize(self.cfg.initialize())

    def test_dataset_generation(self):
        import tempfile, urllib.request, ssl
        ################################################################################################################
        #f = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        #f.write(urllib.request.urlopen("https://www.byte-by-byte.com/wp-content/uploads/2019/01/50-Coding-Interview-Questions.pdf", context=ssl._create_unverified_context()).read())
        #f.close()
        raw_sources = ['C:/Users/AlejandroPrendesCabo/Desktop/proyectos/swarm-intelligence/data/raw/code_interview.pdf']
        ################################################################################################################
        self.main.initialize(self.cfg.initialize())
        updated_config = self.main.dataset_generation(self.cfg.dataset_generation(raw_sources=raw_sources, seeds_chunking_threshold=100))

    def test_dataset_labeling(self):
        self.main.initialize(self.cfg.initialize())

        updated_config = self.main.dataset_labeling(self.cfg.dataset_labeling(update={'n_samples':99999}))

    def test_train(self):
        self.main.initialize(self.cfg.initialize())
        updated_config = self.main.train(self.cfg.train())

    def test_eval(self):
        self.main.initialize(self.cfg.initialize())
        updated_config = self.main.eval(self.cfg.eval())

    def test_predict(self):
        self.main.initialize(self.cfg.initialize())
        config = self.cfg.predict()
        config['user_message'] = 'Simplemente calcula factorial de 10 con el interprete de swarmcompute.'
        updated_config = self.main.predict(config)
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
        self.main.initialize(self.cfg.initialize())
        standby_thread = threading.Thread(target=self.main.telegram_chatbot_run(), args=(self.cfg.telegram_chatbot_run(),), daemon=True)
        standby_thread.start()
        time.sleep(5)

    def test_launch_frontend(self):
        import threading
        import time
        self.main.initialize(self.cfg.initialize())
        standby_thread = threading.Thread(target=self.main.launch_frontend, args=(self.cfg.launch_frontend(),), daemon=True)
        standby_thread.start()
        time.sleep(5000)
