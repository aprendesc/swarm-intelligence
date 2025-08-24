from swarmintelligence.main import Main
from swarmintelligence.configs.base_config import Config
import unittest

class TestMain(unittest.TestCase):
    def setUp(self):
        self.test_time = 100
        self.cfg = Config()
        self.main = Main()

    def test_under_development(self):
        print('Development  test')