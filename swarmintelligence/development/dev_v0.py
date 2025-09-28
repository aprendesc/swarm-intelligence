import os

import pandas as pd

from eigenlib.utils.setup import Setup
Setup().init()

"""Basic agent call client level"""
if False:
    from swarmintelligence.modules.general_agent import GeneralAgent
    system_prompt = """
Eres un agente cantarin, que canta todo lo que dice.
    """
    agent = GeneralAgent(system_prompt=system_prompt, model='gpt-4.1', client='oai_1', temperature=1)
    memory = agent.initialize()
    memory, answer = agent.call(memory=memory, user_message='Hola!')
    print(answer)


"""Run telegram chatbot"""
if False:
    from dotenv import load_dotenv
    load_dotenv()
    from swarmintelligence.modules.telegram_chatbot import TelegramChatbotClass
    from swarmintelligence.main import Main
    from swarmintelligence.configs.notion_agent_config import Config

    main = Main()
    cfg = Config()
    main.initialize(cfg.initialize())
    def mi_chat_function(mensaje: str, contexto: dict) -> str:
        cfg = Config().predict()
        cfg['user_message'] = mensaje
        main = Main().predict(cfg)
        return main['agent_message']

    TOKEN = os.environ['TELEGRAM_BOT_TOKEN_1']  # Reemplázalo con el token de @BotFather
    bot = TelegramChatbotClass(token=TOKEN, chat_function=mi_chat_function)

    # 3. Inicia el bot
    if __name__ == "__main__":
        bot.run(polling=True)  # Esto arranca el bot en modo polling


"""Basic agent call agent abstraction level"""
if False:
    from swarmintelligence.modules.swarm_intelligence_agent import SwarmIntelligenceAgent
    agent = SwarmIntelligenceAgent()
    memory = agent.initialize()
    memory, answer = agent.call(memory=memory, user_message='Ejecuta factorial de 10 en consola de python.')
    memory, answer = agent.call(memory=memory, user_message='Ejecuta un "hola mundo" en la consola bash a modo de prueba')

"""Vector Database"""
if False:
    from eigenlib.genai.vector_database import VectorDatabase


from datetime import date
hoy = date.today()
hoy_str = hoy.strftime("%Y-%m-%d")




if __name__ == '__main__':
    from swarmintelligence.modules.swarm_intelligence_agent import SwarmIntelligenceAgent

    agent = SwarmIntelligenceAgent()
    memory = agent.initialize()
    memory, answer = agent.call(memory=memory, user_message='Ejecuta factorial de 10 en consola de python.')

if True:
    from eigenlib.genai.embeddings_client import EmbeddingsClient
    import numpy as np

    class MemoryManager:
        def __init__(self):
            self.ec = EmbeddingsClient()
            self.ec.initialize()
            self.memory_threshold = 10000

        def get(self, history, query):
            history['cum_tokens'] = history['n_tokens'].iloc[::-1].cumsum().iloc[::-1]

            # SHORT TERM MEMORY
            history['cum_tokens'] = history['n_tokens'].iloc[::-1].cumsum().iloc[::-1]
            st_history = history[(history["role"] == "system") | (history["cum_tokens"] <= self.memory_threshold)]
            lt_history = history[(history["role"] == "system") | (history["cum_tokens"] > self.memory_threshold)]

            # LONG TERM MEMORY
            emb = self.ec._get_embedding(query)
            history['embedding'] = history['embedding'].apply(lambda x: eval(x))
            df_result = self.ec.get_similarity(history, "embedding", query, sort=False)
            lt_history = self.select_top_messages_with_neighbors_optimized(df_result=df_result, top_n=100, neighbor_window=10)

            history = pd.concat([lt_history, st_history])

            return history

        def select_top_messages_with_neighbors_optimized(self, df_result, top_n=100, neighbor_window=10):
            """
            Versión optimizada usando operaciones vectorizadas.
            """

            df_sorted = df_result.sort_values('timestamp').reset_index(drop=True)

            # Obtener los índices de los top_n mensajes
            top_indices = df_sorted.nlargest(top_n, 'score').index.values

            # Crear matriz de rangos para todos los top messages
            ranges = np.column_stack([
                np.maximum(0, top_indices - neighbor_window),
                np.minimum(len(df_sorted), top_indices + neighbor_window + 1)
            ])

            # Crear array booleano para marcar qué índices mantener
            keep_mask = np.zeros(len(df_sorted), dtype=bool)

            for start, end in ranges:
                keep_mask[start:end] = True

            # Filtrar el DataFrame
            filtered_df = df_sorted[keep_mask].copy()

            # Marcar los mensajes top originales
            filtered_df['is_top_message'] = filtered_df.index.isin(top_indices)

            return filtered_df
