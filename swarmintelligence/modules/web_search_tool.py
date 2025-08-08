from eigenlib.LLM.intelligent_web_search import IntelligentWebSearch
import json

class WebSearchTool:
    def __init__(self):
        self.name = "intelligent_web_search"
        self.description = "Makes a deep web search and gets the results."
        self.args = [
            {
                "name": "query",
                "type": "string",
                "description": "Text of the query for the web search, it admits complex and simple queries.",
                "required": True,
            },
            {
                "name": "num_results",
                "type": "integer",
                "description": "Maximum number of results to get with a maximum of 10. Higher number for a deeper search. Default 3",
                "required": True,
            },
        ]

    def initialize(self):
        pass

    def get_tool_dict(self):
        tool_name = self.name
        tool_description = self.description
        tool_args = self.args
        args_schema = {}
        required = []
        for arg in tool_args:
            args_schema[arg["name"]] = {
                "type": arg["type"],
                "description": arg["description"],
            }
            if arg.get("required"):
                required.append(arg["name"])
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": args_schema,
                    "required": required,
                },
            },
        }

    def run(self, query, num_results=5):
        num_results = max(1, min(int(num_results), 10))
        search_engine = IntelligentWebSearch()
        raw_results = search_engine.run(query, num_results=num_results)
        return json.dumps({"search_results": raw_results,}, indent=2)
