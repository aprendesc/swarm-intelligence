from swarmintelligence.modules.web_search_tool import WebSearchTool
import unittest

class TestWebSearchTool(unittest.TestCase):
    def setUp(self):
        pass

    def test_web_search_tool(self):
        import json
        ################################################################################################################
        tool = WebSearchTool()
        out = tool.run(query="openai gpt-4", num_results=3)
        print(json.loads(out))
