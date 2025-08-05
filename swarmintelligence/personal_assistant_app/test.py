import unittest
from eigenlib.utils.project_setup import ProjectSetupClass
from swarmintelligence.personal_assistant_app.main import MainClass
from swarmintelligence.personal_assistant_app.config import test_config as config
ProjectSetupClass(project_name='swarmintelligence', app_name='personal_assistant')

class TestMain(unittest.TestCase):
    def setUp(self):
        self.main = MainClass(config)
        self.config = config

    def test_initialize(self):
        updated_config = self.main.initialize(self.config)

    def test_tools_setup(self):
        updated_config = self.main.tools_setup(self.config)

    def test_dataset_generation(self):
        updated_config = self.main.dataset_generation(self.config)

    def test_dataset_labeling(self):
        updated_config = self.main.dataset_labeling(self.config)

    def test_train(self):
        updated_config = self.main.train(self.config)

    def test_eval(self):
        updated_config = self.main.eval(self.config)

    def test_predict(self):
        self.main.initialize(self.config)
        self.config['user_message'] = 'Busca en las fuentes el significado de Lorem Ipsum'
        updated_config = self.main.predict(self.config)
        print(updated_config['state_dict']['answer'])

    def test_telegram_chatbot_run(self):
        updated_config = self.main.telegram_chatbot_run(self.config)

    def test_launch_front(self):
        updated_config = self.main.launch_front(self.config)

    #TEST UNDER DEVELOPMENT#############################################################################################
    def test_under_development(self):
        pass

if __name__ == '__main__':
    unittest.main()