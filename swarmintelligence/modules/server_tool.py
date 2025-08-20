import json
from swarmcompute.main import MainClass as SCMainClass

class ServerTool:
    def __init__(self, method, default_config, tool_name, tool_description, tool_args):
        self.method = method
        self.tool_name = tool_name
        self.tool_description = tool_description
        self.tool_args = tool_args
        self.default_config = default_config

    def initialize(self):
        pass

    def run(self, config):
        config = config | self.default_config
        try:
            sc_config = {
                'mode': 'client',
                'master_address': 'tcp://localhost:5005',
                'password': 'internal_pass',
                'node_name': 'client_node',
                'node_method': None,
                'address_node': config['selected_project'],
                'payload': {'method': self.method, 'config': config},
                'delay': 0.1,
            }
            sc_main = SCMainClass(sc_config)
            new_config = sc_main.launch_personal_net(sc_config)['response']
            results = new_config['result']
        except Exception as e:
            results = {'error':str(e) + '->The tool server failed. Stop the execution and inform the user.'}
        return json.dumps(results)

    def get_tool_dict(self):
        tool_name = self.tool_name
        tool_description = self.tool_description
        tool_args = self.tool_args
        args_schema = {}
        required = []
        for arg in tool_args:
            args_schema[arg["name"]] = {
                "type": arg["type"],
                "description": arg["description"],
            }
            if arg.get("required"):
                required.append(arg["name"])
            if "items" in arg.keys():
                args_schema[arg["name"]]['items'] = arg['items']
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
