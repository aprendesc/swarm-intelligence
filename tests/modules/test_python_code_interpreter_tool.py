from swarmintelligence.modules.python_code_interpreter_tool import PythonCodeInterpreterToolClass
import unittest

class TestPythonCodeInterpreterToolClass(unittest.TestCase):
    def setUp(self):
        from eigenlib.utils.project_setup import ProjectSetupClass
        ProjectSetupClass(project_folder='swarm-intelligence', test_environ=True)

    def test_python_code_interpreter_tool(self):
        print(PythonCodeInterpreterToolClass(timeout_seconds=5).run(code_str='print("Hola mundo")'))
