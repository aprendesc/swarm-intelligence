from eigenlib.utils.testing_utils import TestUtils
TestUtils().get_coverage('./swarmintelligence')

#LAUNCHERS##############################################################################################################
if True:
    from swarmintelligence.main import MainClass
    from swarmintelligence.configs.test_config import test_config as config
    from swarmintelligence.configs.config import code_assistant_config as config

    main = MainClass(config)
    main.initialize(config)
    #main.tools_setup(config)
    #main.dataset_generation(config)
    #main.dataset_labeling(config)
    #main.train(config)
    #main.eval(config)
    config['user_message'] = 'Busca el tiempo el Alpedrete'
    main.predict(config)
    #main.telegram_chatbot_run(config)
    #main.launch_front(config)

    if __name__ == "__main__":
        pass


if False:
    from swarmintelligence.modules.get_project_map import GetProjectMap
    import unittest

    class TestMainClass(unittest.TestCase):
        def setUp(self):
            pass

        def test_run(self):
            pass

    if __name__ == "__main__":
        unittest.main()