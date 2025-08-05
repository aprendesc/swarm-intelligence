import unittest
from swarmintelligence.automations_app.main import MainClass
from swarmintelligence.automations_app.config import active_config as config
from eigenlib.utils.project_setup import ProjectSetupClass
ProjectSetupClass(project_name='swarmintelligence', app_name='automations')

class TestMain(unittest.TestCase):
    def setUp(self):
        self.main = MainClass(config)
        self.config = config

    def test_computer_use_automation(self):
        self.main.computer_use_automation(self.config)

    def test_standby(self):
        self.main.standby(self.config)

    def test_call_to_notion(self):
        self.main.call_to_notion(self.config)

    def test_listen_smartwatch_notes(self):
        self.main.listen_smartwatch_notes(self.config)

    def test_youtube_to_notion(self):
        self.main.youtube_to_notion(self.config)

    def test_podcast_generation(self):
        updated_config = self.main.podcast_generation(self.config)

    def test_launch_personal_server(self):
        self.main.launch_personal_server(self.config)
        self.main.launch_personal_server_node(self.config)
        config = self.main.call_personal_server_node(self.config)
        print(config['result'])

    #-------------------------------------------------------------------------------------------------------------------
    def test_datasets_load(self):
        from eigenlib.utils.data_utils import DataUtilsClass
        import os
        ################################################################################################################
        print('RAW: ', os.listdir('./data/raw'))
        print('CURATED: ', os.listdir('./data/curated'))

        # CURATED SOURCEs
        input_dataset_name = config['vdb_name']
        df = DataUtilsClass().load_dataset(path=os.environ['CURATED_DATA_PATH'], dataset_name=input_dataset_name, format='pkl', cloud=False)
        input_dataset_name = config['seeds_dataset_name']
        df = DataUtilsClass().load_dataset(path=os.environ['CURATED_DATA_PATH'], dataset_name=input_dataset_name, format='csv', cloud=False)
        input_dataset_name = config['gen_output_dataset_name']
        df = DataUtilsClass().load_dataset(path=os.environ['CURATED_DATA_PATH'], dataset_name=input_dataset_name, format='csv', cloud=False)

    def test_call_served_LLM(self):
        class OSLLMClientClass:
            def __init__(self):
                from eigenlib.utils.general_purpose_net import GeneralPurposeNetClass
                node_ip = '95.18.166.44'
                port = 5005
                password = 'youshallnotpass'
                ################################################################################################################
                self.client_node = GeneralPurposeNetClass()
                self.client_node.start_node(node_name="client_node", server_address=node_ip + ":" + str(port), password=password, method=lambda a, b: a + b)

            def run(self, history):
                result = self.client_node.call_node("phi4-serving", {'history': history})
                return result
        LLM = OSLLMClientClass()
        answer = LLM.run([{'role': 'user', 'content': 'De que color es el caballo blanco de santiago?'}])
        print(answer)

    def test_security_node(self):
        from swarmintelligence.automations_app.main import MainClass
        from swarmintelligence.automations_app.config import active_config as config
        from eigenlib.utils.encryption_utils import EncryptionUtilsClass
        ################################################################################################################
        EU = EncryptionUtilsClass()
        public_key = EU.initialize()
        ################################################################################################################
        config['node_ip'] = '95.18.166.44'
        config['address_node_name'] = 'security_node'
        config['node_call_payload'] = {'public_key':public_key}
        config['password'] = None
        ################################################################################################################
        print('Ensure the server is up.')
        main = MainClass(config)
        config = main.call_personal_server_node(config)
        print(config['result'])

    #TEST UNDER DEVELOPMENT###################################################################################################################
    def test_under_development(self):

        pass


if __name__ == '__main__':
    unittest.main()



