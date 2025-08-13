import unittest
from unittest.mock import patch, MagicMock
from swarmintelligence.configs.test_config import test_config as config
from swarmintelligence.modules.cli import CLI

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('swarmintelligence.modules.cli.MainClass', autospec=True)
        self.MockMainClass = self.patcher.start()
        self.mock_main_instance = self.MockMainClass.return_value
        self.cli = CLI()

    def tearDown(self):
        self.patcher.stop()

    @patch('builtins.input', side_effect=['7'])
    @patch('builtins.print')
    def test_run_calls_etl(self, mock_print, mock_input):
        with patch.object(self.cli, 'run', wraps=self.cli.run) as wrapped_run:
            self.cli.main.ETL = MagicMock()
            try:
                self.cli.run()
            except StopIteration:
                pass
            self.cli.main.predict.assert_called_once_with(config)
