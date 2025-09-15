"""Config"""

class Config:
    def __init__(self, version='v5', sample=None):
        # DATASET
        from jedipoc.modules.env_config_escandallos_dataset_generator import EnvConfigEscandallosDatasetGenerator
        self.gen = EnvConfigEscandallosDatasetGenerator()
        self.dataset_size = 3
        # LABELING
        from jedipoc.modules.purchase_agent_synth_user import PurchaseAgentSynthUser
        from jedipoc.modules.cost_breakdown_agent import CostBreakDownAgent
        self.user = PurchaseAgentSynthUser()
        self.agent = CostBreakDownAgent()
        self.env_config_dataset = './data/processed/escandallos_assistant_dataset'
        self.env_config_history = './data/processed/escandallos_assistant_history'
        #FINE TUNING
        self.ft_dataset = './data/processed/ft'
        self.ft_model = 'gpt-4.1'
        self.tools_register = ''
        # GENERAL
        self.version = version
        self.sample = sample

    def initialize(self, update=None):
        cfg = {
            'agent': self.agent,
        }
        return cfg | (update or {})

    def dataset_generation(self, update=None):
        cfg = {
            'gen': self.gen,
            'dataset_size': self.dataset_size,
            'output_dataset_path': self.env_config_dataset,
        }
        return cfg | (update or {})

    def dataset_labeling(self, update=None):
        cfg = {
            'env_config_input_dataset': self.env_config_dataset,
            'env_config_input_history': self.env_config_history,
            'user': self.user,
            'agent': self.agent,
            'env_config_output_dataset': self.env_config_dataset,
            'env_config_output_history': self.env_config_history,
        }
        return cfg | (update or {})

    def train(self, update=None):
        cfg = {
            'env_config_input_history': self.env_config_history,
            'ft_dataset_name': self.ft_dataset,
            'perc_split': 0.2,
            'run_ft': True,
            'n_epochs': 2,
            'ft_model': self.ft_model,
            'tools': self.tools_register
        }
        return cfg | (update or {})

    def eval(self, update=None):
        cfg = {
            'env_config_input_dataset': self.env_config_dataset,
            'user': self.user,
            'agent': self.agent,
            'env_config_output_dataset': self.env_config_dataset,
            'env_config_output_history': self.env_config_history,
        }
        return cfg | (update or {})

    def predict(self, update=None):
        cfg = {
            'user_message': 'Cuanto es 2 + 2?',
            'memory': [],
        }
        return cfg | (update or {})

    def launch_frontend(self, update=None):
        cfg = {'channels': ['COST_BREAKDOWN_AGENT']}
        return cfg | (update or {})


