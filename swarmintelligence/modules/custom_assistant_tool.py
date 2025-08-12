from eigenlib.LLM.episode import EpisodeClass
from swarmintelligence.main import MainClass
import pandas as pd

class CustomAssistantTool:
    def __init__(self, config, tool_description):
        self.config = config
        self.name = config['assistant_name']
        self.description = tool_description
        self.args = [
            {
                "name": "query",
                "type": "string",
                "description": "Message or query that the expert must solve. Put it as clear well specified instructions explaining the full question.",
                "required": True
            }
        ]

    def initialize(self):
        self.episode = EpisodeClass()
        self.main = MainClass(self.config)
        self.main.initialize(self.config)

    def get_tool_dict(self):
        args_dict = {}
        required_list = []
        for a in self.args:
            arg_name = a['name']
            arg_type = a['type']
            arg_description = a['description']
            if a['required']:
                required_list.append(arg_name)
            args_dict[arg_name] = {"type": arg_type, "description": arg_description}
        return {"type": "function", "function": {"name": self.name, "description": self.description, "parameters": {"type": "object", "properties": args_dict, "required": required_list}}}

    def run(self, query):
        self.config["history"] = self.episode.history.to_dict(orient='records')
        self.config["user_message"] = query
        updated_config = self.main.predict(self.config)
        self.episode.history = pd.DataFrame(updated_config['history'])
        return updated_config['state_dict']['answer']
