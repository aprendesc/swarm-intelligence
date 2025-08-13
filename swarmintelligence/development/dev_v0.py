import unittest
from eigenlib.utils.testing_utils import TestUtils
TestUtils().get_coverage('./swarmintelligence')


from swarmintelligence.main import MainClass
from swarmintelligence.configs.test_config import test_config as config

main = MainClass(config)







#MODULE##########################################################################################################
class MainModule:
    def __init__(self):
        pass

    def run(self, argument_1, argument_2):
        output = argument_1 + argument_2
        return output

#CONFIGURATION##########################################################################################################
config = {
    'argument_1': 1,
    'argument_2': 1,
    }

#LAUNCHER###############################################################################################################
class TestMainModule(unittest.TestCase):
    def setUp(self):
        pass

    def testrun(config):
        argument_1 = config['argument_1']
        argument_2 = config['argument_2']
        output = MainModule().run(argument_1, argument_2)
        config['output'] = output
        return config


if __name__ == "__main__":
    MainModule.run()