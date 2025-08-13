"""Loader Script"""
if True:
    import sys
    import os
    from dotenv import load_dotenv
    ####################################################################################################################
    project_folder = 'swarm-intelligence'
    base_path = f'C:/Users/{os.environ["USERNAME"]}/Desktop/proyectos'
    ####################################################################################################################
    load_dotenv()
    os.getcwd()
    sys.path.extend([
        os.path.join(base_path, 'swarm-ml'),
        os.path.join(base_path, 'swarm-intelligence'),
        os.path.join(base_path, 'swarm-automations'),
        os.path.join(base_path, 'swarm-compute'),
        os.path.join(base_path, 'eigenlib')
    ])
    os.environ['PROJECT_NAME'] = project_folder.replace('-', '')
    os.environ['PROJECT_FOLDER'] = project_folder
    os.chdir(os.path.join(base_path, project_folder))

########################################################################################################################
"""Test Coverage"""
if True:
    from eigenlib.utils.testing_utils import TestUtils

    _, coverage = TestUtils().get_coverage('./' + os.environ['PROJECT_NAME'])
    assert int(coverage) == 100

########################################################################################################################
"""Launch main"""
if False:
    from swarmintelligence.main import MainClass
    from swarmintelligence.configs.test_config import test_config as config

    main = MainClass(config)
    main.ETL(config)
    # main.train(config)
    # main.hparam_tuning(config)
    # main.eval(config)
    # main.predict(config)

########################################################################################################################
"""Run all tests"""
if False:
    from dotenv import load_dotenv
    import unittest

    load_dotenv()
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='./tests/modules', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

########################################################################################################################
"""Launch dummy development code."""
if False:
    class MainModule:
        def __init__(self):
            pass

        def run(self, argument_1, argument_2):
            output = argument_1 + argument_2
            return output


    print(MainModule().run(1, 2))

    import unittest


    class TestMainModule(unittest.TestCase):
        def setUp(self):
            pass

        def test_run(self):
            ################################################################################################################
            config = {
                'argument_1': 1,
                'argument_2': 1,
            }
            ################################################################################################################
            argument_1 = config['argument_1']
            argument_2 = config['argument_2']
            output = MainModule().run(argument_1, argument_2)
            config['output'] = output
            return config


    test = TestMainModule()
    test.setUp()
    test.test_run()

