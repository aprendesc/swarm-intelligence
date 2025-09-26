from eigenlib.genai.embeddings_client import EmbeddingsClient
import numpy as np
import pandas as pd

class MemoryManager:
    def __init__(self):
        self.ec = EmbeddingsClient()
        self.ec.initialize()
        self.memory_threshold = 10000

    def get(self, history, query, id, use_steering=True):

        # CHANNEL SELECTION
        history = history[history['channel'] == id]

        # STEERING MANAGEMENT
        last_false_idx = history[history['steering'] == True].index.max()
        history = history[(history['steering'] == False) | (history.index == last_false_idx)]


        # SHORT TERM MEMORY
        history['cum_tokens'] = history['n_tokens'].iloc[::-1].cumsum().iloc[::-1]
        st_history = history[(history["role"] == "system") | (history["cum_tokens"] <= self.memory_threshold)]
        lt_history = history[(history["cum_tokens"] > self.memory_threshold)]

        # LONG TERM MEMORY
        try:
            history['embedding'] = history['embedding'].apply(lambda x: eval(x))
        except:
            pass
        if len(lt_history) > 0:
            lt_history = self.ec.get_similarity(lt_history, "embedding", query, sort=False)
            lt_history = self.select_top_messages_with_neighbors_optimized(df_result=lt_history, top_n=100, neighbor_window=10)
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


if __name__ == "__main__":
    import random
    import datetime

    mm = MemoryManager()
    aux = mm.get(memory.history, 'factorial')

    num_messages = 20
    roles = ["user", "assistant", "system"]

    data = {
        "role": [random.choice(roles) for _ in range(num_messages)],
        "n_tokens": [random.randint(5, 50) for _ in range(num_messages)],
        "embedding": [str(list(np.random.rand(5))) for _ in range(num_messages)],  # embeddings simulados
        "timestamp": [datetime.datetime.now() - datetime.timedelta(minutes=i) for i in range(num_messages)]
    }

    history = pd.DataFrame(data)

    # Instanciar MemoryManager
    mm = MemoryManager()

    # Consulta de prueba
    query = "Ejemplo de consulta de usuario"

    # Obtener la memoria filtrada
    result = mm.get(history, query)

    print("=== HISTORIAL FILTRADO ===")
    print(result)
