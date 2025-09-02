import json
import os

class ServerTool:
    def __init__(self, method, default_config, tool_name, tool_description, tool_args):
        self.method = method
        self.tool_name = tool_name
        self.tool_description = tool_description
        self.tool_args = tool_args
        self.default_config = default_config
        self.server_config = {
            'master_address': "localhost:5001",
            'client_name': os.environ['PACKAGE_NAME'] + '_client',
            'password': 'test_pass',
            'delay': 1,
            'target_node': 'swarmautomations_node',
            'payload': {},
        }

    def initialize(self):
        pass

    def run(self, config):
        config = config | self.default_config
        try:
            server_config = self.server_config
            server_config['payload'] = {'method': self.method, 'config': config}
            results = self._call_MCP_server(server_config)['result']
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

    def _call_MCP_server(self, config):
        from eigenlib.utils.network_io import NetworkIO
        ################################################################################################################
        MASTER_ADDRESS = config['master_address']
        client_name = config['client_name']
        delay = config['delay']
        password = config['password']
        target_node = config['target_node']
        payload = config['payload']
        ################################################################################################################
        client = NetworkIO()
        client.launch_node(node_name=client_name, master_address=MASTER_ADDRESS, node_method=lambda: "OK", delay=delay, password=password)
        resultado = client.call(target_node=target_node, payload=payload)
        client.stop()
        config['result'] = resultado
        print(resultado)
        return config