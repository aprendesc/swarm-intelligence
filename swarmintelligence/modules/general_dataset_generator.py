import pandas as pd
import numpy as np
from eigenlib.utils.dataset_io import DatasetIO


class EnvConfigGeneralDatasetGenerator:
    def __init__(self):
        pass

    def run(self, dataset_size=100, n_turns=5, max_turns=5):
        df = self.generate_dataset(n=dataset_size, n_turns=n_turns, max_turns=max_turns)
        return df

    def generate_dataset(self, n=20, n_turns=5, max_turns=5):
        difficulty_options = ["facil", "medio", "dificil", "muy dificil"]
        difficulty_probabilities = [0.4, 0.3, 0.15, 0.15]
        difficulties = np.random.choice(difficulty_options, size=n, p=difficulty_probabilities)
        df = pd.DataFrame({
            "episode_id": range(n),
            "max_steps": max_turns,
            "difficulty": difficulties,
            "steering": ["NONE"] * n,
            "user_message": ["NONE"] * n,
            "agent_message": ["NONE"] * n,
            "target": ["NONE"] * n,
            "score": ["NONE"] * n,
            "evaluation": ["NONE"] * n,
        })
        df = df.loc[df.index.repeat(n_turns)].reset_index(drop=True)
        df["step"] = np.tile(range(0, n_turns), n)
        df['update'] = True
        df = df[['episode_id', 'step', 'max_steps', 'difficulty', 'steering', 'user_message', 'agent_message', 'target','score', 'evaluation', 'update']]
        return df

if __name__ == "__main__":
    epigen = EnvConfigEscandallosDatasetGenerator()
    dataset_df = epigen.run(n=100, n_turns=1, max_turns=1)
    DatasetIO().create(path='./data/processed/test_genai_dataset', dataframe=dataset_df, partition_format='xlsx', overwrite=True)