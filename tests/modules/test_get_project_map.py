from swarmintelligence.modules.get_project_map import GetProjectMap
import unittest

class TestMainClass(unittest.TestCase):
    def setUp(self):
        pass

    def test_run(self):
        project_dir = '.'
        flat_map, tree_map = GetProjectMap().run(project_dir)
        print(tree_map)
        for line in GetProjectMap().ascii_pretty(tree_map):
            print(line)