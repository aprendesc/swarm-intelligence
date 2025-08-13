from swarmintelligence.modules.web_search_tool import WebSearchTool
import unittest

class TestWebSearchTool(unittest.TestCase):
    def setUp(self):
        pass

    def test_web_search_tool(self):
        import json
        ################################################################################################################
        tool = WebSearchTool()
        out = tool.run(query="tiempo Alpedrete ahora", num_results=5)
        print(json.loads(out))
