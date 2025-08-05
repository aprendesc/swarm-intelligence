import os
import pandas as pd
from eigenlib.utils.databricks_serving_utils import use_endpoint
from eigenlib.utils.project_setup import ProjectSetupClass
ProjectSetupClass(project_folder='swarm-intelligence')

class MainClass:
    def __init__(self, config={}):
        self.hypothesis = config['hypothesis']
        self.use_cloud = config['use_cloud']
        self.use_wandb = config['use_wandb']

    @use_endpoint
    def initialize(self, config):
        from eigenlib.LLM.rag_chain import RAGChain
        ################################################################################################################
        agent_model = config['agent_model']
        user_model = config['user_model']
        eval_model = config['eval_model']
        user_reasoning_effort = config['user_reasoning_effort']
        agent_reasoning_effort = config['agent_reasoning_effort']
        eval_reasoning_effort = config['eval_reasoning_effort']
        temperature = config['temperature']
        tools_dict = config['tools_dict']
        tool_choice = config['tool_choice']
        ################################################################################################################
        self.chain = RAGChain(agent_model=agent_model, user_model=user_model, eval_model=eval_model, user_reasoning_effort=user_reasoning_effort, agent_reasoning_effort=agent_reasoning_effort, eval_reasoning_effort=eval_reasoning_effort, tools_dict=tools_dict, tool_choice=tool_choice)
        self.chain.initialize()
        return config

    @use_endpoint
    def tools_setup(self, config):
        from eigenlib.LLM.vector_database import VectorDatabaseClass
        from eigenlib.LLM.sources_parser import SourcesParserClass
        from eigenlib.utils.data_utils import DataUtilsClass
        import os
        ################################################################################################################
        if True:
            ############################################################################################################
            raw_sources = config['raw_sources']
            lang = config['lang']
            VDB_name = config['vdb_name']
            vdb_chunking_threshold = config['vdb_chunking_threshold']
            ############################################################################################################
            df = SourcesParserClass().run_batch(raw_sources, lang=lang)
            #INDEXATION
            VDB = VectorDatabaseClass(content_feature='steering')
            VDB.initialize()
            source_df = VDB.create(df['content'].sum(), separator='.', create_vectors=True, chunking_threshold=vdb_chunking_threshold)
            DataUtilsClass().save_dataset(source_df, path=os.environ['CURATED_DATA_PATH'], dataset_name=VDB_name, format='pkl', cloud=self.use_cloud)
        return config

    @use_endpoint
    def dataset_generation(self, config):
        from eigenlib.LLM.vector_database import VectorDatabaseClass
        from eigenlib.LLM.sources_parser import SourcesParserClass
        from eigenlib.utils.data_utils import DataUtilsClass
        import os
        ################################################################################################################
        raw_sources = config['raw_sources']
        lang = config['lang']
        seeds_dataset_name = config['seeds_dataset_name']
        seeds_chunking_threshold = config['seeds_chunking_threshold']
        ################################################################################################################
        df = SourcesParserClass().run_batch(raw_sources, lang=lang)
        #INDEXATION
        VDB = VectorDatabaseClass(content_feature='steering')
        source_df = VDB.create(df['content'].sum(), separator='.', create_vectors=False, chunking_threshold=seeds_chunking_threshold)
        DataUtilsClass().save_dataset(source_df, path=os.environ['CURATED_DATA_PATH'], dataset_name=seeds_dataset_name, format='csv', cloud=self.use_cloud)
        return config

    @use_endpoint
    def dataset_labeling(self, config):
        from eigenlib.utils.data_utils import DataUtilsClass
        from eigenlib.LLM.dataset_autolabeling import DatasetAutolabelingClass
        ################################################################################################################
        input_dataset_name = config['gen_input_dataset_name']
        output_dataset_name = config['gen_output_dataset_name']
        static_user = config['gen_static_user']
        max_iter = config['gen_max_iter']
        use_agent_steering = config['gen_use_agent_steering']
        hist_output_dataset_name = config['hist_output_dataset_name']
        n_thread = config['n_thread']
        use_guidance = config['use_guidance']
        gen_n_epoch = config['gen_n_epoch']
        ################################################################################################################
        self.initialize(config)
        ################################################################################################################
        match use_guidance:
            case True:
                df = DataUtilsClass().load_dataset(path=os.environ['CURATED_DATA_PATH'], dataset_name=input_dataset_name, format='csv', file_features=False, cloud=False).applymap(lambda x: None if pd.isna(x) else x)
                assert list(df.columns) == [
                    'index',
                    'episode_id',
                    'n_tokens',
                    'step',
                    'steering',
                    'img',
                    'user_message',
                    'agent_message',
                    'target',
                    'score',
                    'analysis'
                ], "Las columnas del DataFrame no coinciden exactamente con las esperadas"
                df = df.sample(min(config['n_samples'], len(df)))
            case False:
                df = pd.DataFrame({
                'index': [None] * gen_n_epoch,
                'episode_id': [None] * gen_n_epoch,
                'n_tokens': [None] * gen_n_epoch,
                'step': [None] * gen_n_epoch,
                'steering': [None] * gen_n_epoch,
                'img': [None] * gen_n_epoch,
                'user_message': [None] * gen_n_epoch,
                'agent_message': [None] * gen_n_epoch,
                'target': [None] * gen_n_epoch,
                'score': [None] * gen_n_epoch,
                'analysis': [None] * gen_n_epoch
            })

        fixed_dict = {
            'user_context': config['user_context'],
            'user_instructions': config['user_instructions'],
            'agent_context': config['agent_context'],
            'agent_instructions': config['agent_instructions'],
            'eval_instructions': config['eval_instructions']
        }
        df, history = DatasetAutolabelingClass().run(df, self.chain, fixed_dict, max_iter=max_iter, static_user=static_user, use_agent_steering=use_agent_steering, use_wandb=self.use_wandb, n_thread=n_thread)
        DataUtilsClass().save_dataset(df, path=os.environ['CURATED_DATA_PATH'], dataset_name=output_dataset_name, format='csv', cloud=self.use_cloud)
        DataUtilsClass().save_dataset(history, path=os.environ['CURATED_DATA_PATH'], dataset_name=hist_output_dataset_name, format='csv', cloud=self.use_cloud)
        return config

    @use_endpoint
    def train(self, config):
        from eigenlib.utils.data_utils import DataUtilsClass
        from eigenlib.LLM.oai_llm import OAILLMClientClass
        from eigenlib.LLM.llm_validation_split import LLMValidationSplitClass
        import os
        ################################################################################################################
        gen_dataset_name = config['hist_output_dataset_name']
        ft_dataset_name = config['ft_dataset_name']
        perc_split = config['perc_split']
        run_ft = config['run_ft']
        n_epochs = config['n_epochs']
        ft_model = config['ft_model']
        agent_id = 'AGENT'
        ################################################################################################################
        df = DataUtilsClass().load_dataset(path=os.environ['CURATED_DATA_PATH'], dataset_name=gen_dataset_name, format='csv', file_features=False, cloud=self.use_cloud).applymap(lambda x: None if pd.isna(x) else x)
        df = df[df['channel'].isin(['system','assistant','user', 'tool' ]) & (df['agent_id'].isin([agent_id]))]
        X_train, X_test = LLMValidationSplitClass().run(df, test_size=perc_split, random_seed=42)
        OAILLMClientClass(model=ft_model).train(X_train=X_train, X_test=X_test, output_FT_dataset_name=ft_dataset_name, agent_id=agent_id, run_ft=run_ft, n_epoch=n_epochs)
        return config

    @use_endpoint
    def eval(self, config):
        from eigenlib.utils.data_utils import DataUtilsClass
        from eigenlib.utils.parallel_utils import ParallelUtilsClass
        from eigenlib.LLM.episode import EpisodeClass
        import wandb
        ################################################################################################################
        input_dataset_name = config['eval_input_dataset_name']
        output_dataset_name = config['eval_output_dataset_name']
        static_user = config['eval_static_user']
        max_iter = config['eval_max_iter']
        use_agent_steering = config['eval_use_agent_steering']
        n_thread = config['n_thread']
        eval_hist_output_dataset_name = config['eval_hist_output_dataset_name']
        ################################################################################################################
        self.initialize(config)
        ################################################################################################################
        self.chain.run_eval = True
        self.chain.static_user = static_user
        self.chain.max_iter = max_iter
        self.chain.use_agent_steering = use_agent_steering
        self.chain.use_wandb = self.use_wandb
        # DATA LOAD######################################################################################################
        df = DataUtilsClass().load_dataset(path=os.environ['CURATED_DATA_PATH'], dataset_name=input_dataset_name, format='csv', file_features=False, cloud=False).applymap(lambda x: None if pd.isna(x) else x)
        if config.get('n_samples') is not None:
            df = df.sample(config.get('n_samples'))
        # GENERATION
        fixed_dict = {
            'user_context': config['user_context'],
            'user_instructions': config['user_instructions'],
            'agent_context': config['agent_context'],
            'agent_instructions': config['agent_instructions'],
            'eval_instructions': config['eval_instructions']
        }
        assert list(df.columns) == [
            'index',
            'episode_id',
            'n_tokens',
            'step',
            'steering',
            'img',
            'user_message',
            'agent_message',
            'target',
            'score',
            'analysis'
        ], "Las columnas del DataFrame no coinciden exactamente con las esperadas"
        if self.use_wandb:
            wandb.login(key=os.environ['WANDB_API_KEY'])
            wandb.init(project=os.environ['project_name'], config={"hypothesis": config['hypothesis']})
        def generation_fun(variable_dict={}):
            state_dict = fixed_dict | variable_dict
            episode = EpisodeClass(state_dict['episode_id'])
            for i in range(10):
                try:
                    episode, state_dict = self.chain.generate(episode, state_dict)
                    break
                except Exception as e:
                    print(e)
                    print('Chain Failed, retrying...')
            return episode.history
        result = ParallelUtilsClass().run_in_parallel(generation_fun, {}, {'variable_dict': df.to_dict(orient='records')}, n_threads=n_thread, use_processes=False)
        # METRICS
        history = pd.concat(result).sort_values(by=['episode_id', 'step', 'timestamp'])
        DataUtilsClass().save_dataset(history, path=os.environ['CURATED_DATA_PATH'], dataset_name=config['eval_hist_output_dataset_name'], format='csv', cloud=self.use_cloud)
        df = history[history['channel'].isin(['assistant']) & (history['agent_id'].isin(['EVAL']))]
        df = pd.json_normalize(df['state_dict'])
        df['episode_id'] = range(len(df))
        df['index'] = range(len(df))
        DataUtilsClass().save_dataset(df, path=os.environ['CURATED_DATA_PATH'], dataset_name=output_dataset_name, format='csv', cloud=self.use_cloud)
        print('========================================================================')
        print('Result score:', df['score'].mean())
        if self.use_wandb:
            wandb.run.summary["mode"] = 'evaluation'
            wandb.run.summary["using_steering"] = use_agent_steering
            wandb.run.summary["mean_score"] = df['score'].mean()
            wandb.run.summary["variance_score"] = df['score'].std()
            wandb.finish()
        return config

    @use_endpoint
    def predict(self, config):
        import pandas as pd
        from eigenlib.LLM.episode import EpisodeClass
        ################################################################################################################
        state_dict = {
                        'agent_context': config['agent_context'],
                        'agent_instructions':config['agent_instructions'],
                        'steering': config['steering'],
                        'img': config['img'],
                        'user_message': config['user_message'],
                        }
        history = config['history']
        ################################################################################################################
        episode = EpisodeClass()
        episode.history = pd.DataFrame(history)
        episode, state_dict = self.chain.predict(episode, state_dict)
        config['state_dict'] = state_dict
        config['history'] = episode.history.to_dict(orient='records')
        return config

    @use_endpoint
    def telegram_chatbot_run(self, config):
        from swarmintelligence.modules.telegram_chatbot import TelegramChatbotClass
        ################################################################################################################
        BOT_TOKEN = "7775699333:AAHYOw3YsEtxgKZg1eUzUCl7lfrEQFnAH5o"
        ################################################################################################################
        self.initialize(config)
        def mi_logica_chat(mensaje, context):
            from swarmintelligence.config import test_config as config
            config['user_message'] = mensaje
            config = self.predict(config)
            answer = config['state_dict']['answer']
            return answer
        bot = TelegramChatbotClass(BOT_TOKEN, mi_logica_chat)
        bot.run()

    def launch_front(self, config):
        import os
        import subprocess
        ################################################################################################################
        file = os.path.join(os.environ['PROJECT_ROOT'], f'{os.environ["PROJECT_NAME"]}/modules/frontend.py')
        eigenlib_root = os.environ["PROJECT_ROOT"].replace(os.environ['PROJECT_FOLDER'], 'eigenlib')
        command = f'set PYTHONPATH={os.environ["PROJECT_ROOT"]};{eigenlib_root} && streamlit run ' + file
        subprocess.run(command, shell=True)
        return config

if __name__ == '__main__':
    from swarmintelligence.config import code_assistant_config as config
    main = MainClass(config)
    #main.initialize(config)
    #main.tools_setup(config)
    #main.dataset_generation(config)
    #main.dataset_labeling(config)
    #main.train(config)
    #main.eval(config)
    #main.predict(config)
    #main.telegram_chatbot_run(config)
    main.launch_front(config)