import pandas as pd
from eigenlib.utils.setup import Setup

class Main:
    def __init__(self):
        Setup().init()

    def initialize(self, config):
        ################################################################################################################
        agent = config['agent']
        ################################################################################################################
        self.agent = agent
        memory = self.agent.initialize()
        ################################################################################################################
        config['history'] = memory.history.to_dict(orient='records')
        return config

    def dataset_generation(self, config):
        from eigenlib.utils.dataset_io import DatasetIO
        ################################################################################################################
        gen = config['gen']
        dataset_size = config['dataset_size']
        output_dataset_path = config['output_dataset_path']
        ################################################################################################################
        dataset_df = gen.run(dataset_size=dataset_size, n_turns=1, max_turns=1)
        DatasetIO().create(path=output_dataset_path, dataframe=dataset_df, partition_format='xlsx', overwrite=True)
        ################################################################################################################
        return config

    def dataset_labeling(self, config):
        from eigenlib.genai.base_simulator import BaseSimulator
        from eigenlib.genai.base_environment import BaseEnvironment
        from eigenlib.utils.dataset_io import DatasetIO
        ################################################################################################################
        env_config_input_dataset = config['env_config_input_dataset']
        env_config_input_history = config['env_config_input_history']
        user = config['user']
        agent = config['agent']
        env_config_output_dataset = config['env_config_output_dataset']
        env_config_output_history = config['env_config_output_history']
        ################################################################################################################
        env_config = DatasetIO().read(path=env_config_input_dataset)
        env_history = DatasetIO().read(path=env_config_input_history)
        history, env_config = BaseSimulator(env=BaseEnvironment(), user=user, agent=agent).generate(env_config=env_config, env_history=env_history)
        DatasetIO().create(path=env_config_output_dataset, dataframe=env_config, partition_format='xlsx', overwrite=True)
        DatasetIO().create(path=env_config_output_history, dataframe=history, partition_format='xlsx', overwrite=True)
        return config

    def train(self, config):
        from eigenlib.utils.dataset_io import DatasetIO
        from eigenlib.LLM.llm_client import LLMClientClass
        from eigenlib.LLM.llm_validation_split import LLMValidationSplitClass
        ################################################################################################################
        env_config_input_history = config['env_config_input_history']
        ft_dataset_name = config['ft_dataset_name']
        perc_split = config['perc_split']
        run_ft = config['run_ft']
        n_epochs = config['n_epochs']
        ft_model = config['ft_model']
        tools = config['tools']
        agent_id = 'AGENT'
        ################################################################################################################
        df = DatasetIO().read(path=env_config_input_history)
        df = df[df['channel'].isin(['system','assistant','user', 'tool' ]) & (df['agent_id'].isin([agent_id]))]
        X_train, X_test = LLMValidationSplitClass().run(df, test_size=perc_split, random_seed=42)
        LLMClientClass(model=ft_model).train(X_train=X_train, X_test=X_test, output_FT_dataset_name=ft_dataset_name, agent_id=agent_id, run_ft=run_ft, n_epoch=n_epochs, tools=tools)
        return config

    def eval(self, config):
        from eigenlib.genai.base_simulator import BaseSimulator
        from eigenlib.genai.base_environment import BaseEnvironment
        from eigenlib.utils.dataset_io import DatasetIO
        ################################################################################################################
        env_config_input_dataset = config['env_config_input_dataset']
        user = config['user']
        agent = config['agent']
        env_config_output_dataset = config['env_config_output_dataset']
        env_config_output_history = config['env_config_output_history']
        ################################################################################################################
        env_config = DatasetIO().read(path=env_config_input_dataset)
        env_config = DatasetIO().read(path=env_config_input_dataset)
        history, env_config = BaseSimulator(env=BaseEnvironment(), user=user, agent=agent).generate(env_config=env_config)
        DatasetIO().create(path=env_config_output_dataset, dataframe=env_config, partition_format='xlsx', overwrite=True)
        DatasetIO().create(path=env_config_output_history, dataframe=history, partition_format='xlsx', overwrite=True)
        return config

    def predict(self, config):
        from eigenlib.genai.memory import Memory
        history = config['history']
        user_message = config['user_message']
        ################################################################################################################
        memory = Memory()
        memory.history = pd.DataFrame(history)
        memory, answer = self.agent.call(memory=memory, user_message=user_message)
        ################################################################################################################
        config['agent_message'] = answer
        config['history'] = memory.history.to_dict(orient='records')
        return config

    def launch_frontend(self, config):
        import os
        from eigenlib.utils.console_io import Console
        ################################################################################################################
        file = os.path.join(os.environ["BASE_PATH"], os.environ['PROJECT_FOLDER'], os.environ['PACKAGE_NAME'], 'modules/frontend.py')
        project_root = os.path.join(os.environ["BASE_PATH"], os.environ['PROJECT_FOLDER'])
        eigenlib_root = os.path.join(os.environ["BASE_PATH"], 'eigenlib')
        Console(backend='cmd').run(command=f'set PYTHONPATH={eigenlib_root};{project_root} && streamlit run ' + file)
        return config

if __name__ == '__main__':
    from swarmintelligence.configs.base_config import Config
    cfg = Config()
    main = Main()
    main.dataset_generation(cfg.dataset_generation())
    main.dataset_labeling(cfg.dataset_labeling())
    #main.train(cfg.train())
    #main.eval(cfg.eval())
    #updated_cfg = main.initialize(cfg.initialize())
    #updated_cfg = main.predict(cfg.predict(update=updated_cfg))
    #print(updated_cfg['agent_message'])
    #cfg = main.launch_frontend(cfg.launch_frontend())

