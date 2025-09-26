import pandas as pd
import os
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

    def validation_split(self, config):
        from eigenlib.LLM.llm_validation_split import LLMValidationSplitClass
        from eigenlib.utils.dataset_io import DatasetIO
        ################################################################################################################
        env_config_dataset = config['env_config_dataset']
        perc_split = config['perc_split']
        env_config_train_dataset = config['env_config_train_dataset']
        env_config_test_dataset = config['env_config_test_dataset']
        ################################################################################################################
        env_config = DatasetIO().read(path=env_config_dataset)
        env_config_train, env_config_test = LLMValidationSplitClass().run(env_config, test_size=perc_split, random_seed=42)

        DatasetIO().create(path=env_config_train_dataset, dataframe=env_config_train, partition_format='xlsx', overwrite=True)
        DatasetIO().create(path=env_config_test_dataset, dataframe=env_config_test, partition_format='xlsx', overwrite=True)
        return config

    def evaluation(self, config):
        from eigenlib.genai.base_simulator import BaseSimulator
        from eigenlib.genai.base_environment import BaseEnvironment
        from eigenlib.utils.dataset_io import DatasetIO
        ################################################################################################################
        experiment_id = config['experiment_id']
        env_config_input_train_dataset = config['env_config_input_train_dataset']
        env_config_input_train_history = config['env_config_input_train_history']
        env_config_input_test_dataset = config['env_config_input_test_dataset']
        env_config_input_test_history = config['env_config_input_test_history']
        user = config['user']
        agent = config['agent']
        run_train_inference = config['run_train_inference']
        run_test_inference = config['run_train_inference']
        env_config_output_train_dataset = config['env_config_output_train_dataset']
        env_config_output_train_history = config['env_config_output_train_history']
        env_config_output_test_dataset = config['env_config_output_test_dataset']
        env_config_output_test_history = config['env_config_output_test_history']
        ################################################################################################################
        # TRAIN LABELING
        if run_train_inference:
            env_train_config = DatasetIO().read(path=env_config_input_train_dataset)
            env_train_history = DatasetIO().read(path=env_config_input_train_history)
            env_train_history, env_train_config = BaseSimulator(env=BaseEnvironment(), user=user, agent=agent, experiment_id=experiment_id).generate(env_config=env_train_config, env_history=env_train_history)
            DatasetIO().create(path=env_config_output_train_dataset, dataframe=env_train_config, partition_format='xlsx', overwrite=True)
            DatasetIO().create(path=env_config_output_train_history, dataframe=env_train_history, partition_format='xlsx', overwrite=True)

        # TEST LABELING
        if run_test_inference:
            env_test_config = DatasetIO().read(path=env_config_input_test_dataset)
            env_test_history = DatasetIO().read(path=env_config_input_test_history)
            env_test_history, env_test_config = BaseSimulator(env=BaseEnvironment(), user=user, agent=agent, experiment_id=experiment_id).generate(env_config=env_test_config, env_history=env_test_history)
            DatasetIO().create(path=env_config_output_test_dataset, dataframe=env_test_config, partition_format='xlsx', overwrite=True)
            DatasetIO().create(path=env_config_output_test_history, dataframe=env_test_history, partition_format='xlsx', overwrite=True)
        return config

    def train(self, config):
        from eigenlib.utils.dataset_io import DatasetIO
        from eigenlib.LLM.llm_client import LLMClientClass
        ################################################################################################################
        env_config_train_history = config['env_config_train_history']
        env_config_test_history = config['env_config_test_history']
        ft_dataset_name = config['ft_dataset_name']
        run_ft = config['run_ft']
        n_epochs = config['n_epochs']
        ft_model = config['ft_model']
        tools = config['tools']
        channel = config['channel']
        ################################################################################################################
        X_train = DatasetIO().read(path=env_config_train_history)
        X_test = DatasetIO().read(path=env_config_test_history)
        LLMClientClass(model=ft_model).train(X_train=X_train, X_test=X_test, output_FT_dataset_name=ft_dataset_name, channel=channel, run_ft=run_ft, n_epoch=n_epochs, tools=tools)
        return config

    def predict(self, config):
        from eigenlib.genai.memory import Memory
        history = config['history']
        user_message = config['user_message']
        ################################################################################################################
        memory = Memory()
        memory.history = pd.DataFrame(history)
        memory, answer = self.agent.call(memory=memory, user_message=user_message)
        print('AGENT: ', answer)
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

    def telegram_chatbot_run(self, config):
        from dotenv import load_dotenv
        load_dotenv()
        from swarmintelligence.modules.telegram_chatbot import TelegramChatbotClass
        from swarmintelligence.configs.notion_agent_config import Config
        cfg = Config()
        self.initialize(cfg.initialize())
        self.predict_cfg = cfg.predict()
        def mi_chat_function(mensaje: str, contexto: dict) -> str:
            self.predict_cfg['user_message'] = mensaje
            self.predict_cfg = self.predict(self.predict_cfg)
            print(self.predict_cfg)
            return self.predict_cfg['agent_message']
        TOKEN = os.environ['TELEGRAM_BOT_TOKEN_2']
        bot = TelegramChatbotClass(token=TOKEN, chat_function=mi_chat_function)
        bot.run(polling=True)  # Esto arranca el bot en modo polling

        import time
        while True:
            time.sleep(1)
            print('Telegram running')

if __name__ == '__main__':
    from swarmintelligence.configs.notion_agent_config import Config
    cfg = Config()
    main = Main()
    #main.dataset_generation(cfg.dataset_generation())
    #main.validation_split(cfg.validation_split())
    #main.evaluation(cfg.train_evaluation())
    #main.train(cfg.train())
    #main.evaluation(cfg.test_evaluation())
    #updated_cfg = main.initialize(cfg.initialize())
    #updated_cfg = main.predict(cfg.predict(update=updated_cfg))
    #print(updated_cfg['agent_message'])
    #print(updated_cfg['agent_message'])
    cfg = main.launch_frontend(cfg.launch_frontend())
    #cfg = main.telegram_chatbot_run(cfg.telegram_chatbot_run())

