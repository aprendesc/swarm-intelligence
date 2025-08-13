from swarmintelligence.modules.code_interpreter_tool import CodeInterpreterToolClass
import unittest

class TestCodeInterpreterToolClass(unittest.TestCase):
    def setUp(self):
        pass

    def test_run(self):
        interpreter_path = r"C:\Users\AlejandroPrendesCabo\Desktop\proyectos\swarm-intelligence\.venv\Scripts\python.exe"
        path_folders = [r"C:\Users\AlejandroPrendesCabo\Desktop\proyectos\swarm-intelligence", r"C:\Users\AlejandroPrendesCabo\Desktop\proyectos\eigenlib"]
        result = CodeInterpreterToolClass(interpreter_path=interpreter_path, path_folders=path_folders).run(programming_language='python', code='print("Hi")')
        print(result)
        result = CodeInterpreterToolClass(interpreter_path=interpreter_path, path_folders=path_folders).run(programming_language='bash', code='echo "Hi"')
        print(result)