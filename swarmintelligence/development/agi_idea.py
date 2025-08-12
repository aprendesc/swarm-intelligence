#AGI 1
import pandas as pd
from eigenlib.utils.project_setup import ProjectSetupClass
ProjectSetupClass(project_folder='swarm-intelligence')

from eigenlib.LLM.llm_client import LLMClientClass
from eigenlib.LLM.episode import EpisodeClass

def get_neighbours(df, n, m):
    top_positions = df['score'].nlargest(n).index
    neighbour_positions = set()
    for pos in top_positions:
        for p in range(pos - m, pos + m + 1):
            if 0 <= p < len(df):  # ensure in bounds
                neighbour_positions.add(p)
    subset_df = df.iloc[sorted(neighbour_positions)]
    return subset_df

from eigenlib.LLM.oai_embeddings import OAIEmbeddingsClass
oaiemb = OAIEmbeddingsClass()
oaiemb.initialize()
teacher_episode = EpisodeClass()
episode = EpisodeClass()
full_memory_episode = EpisodeClass()
long_term_memory = 'Eres un asistente con actitud de aprendizaje. Responde de forma natural como un alumno humano.'
episode.log(channel='system', modality='text', content=long_term_memory, agent_id='AGI1')
teacher_episode.log(channel='system', modality='text', content='Examina al alumno sobre eventos historicos sucedidos en el año 2024 y de los cuales solo se puede tener información habiendo vivido en 2024, con info a posteriori. Si no los sabe o se los inventa corrigele y enseñale y vuelve a examinarle. Obten una nota final despues de cada evaluación y compara las mejoras tras darle las clases. Adopta el tono y actitud de un profesor humano. Haz una pregunta de cada vez, siendo natural.', agent_id='TEACHER')

while True:
    if True:
        user_message = LLMClientClass(model='gpt-5-mini', temperature=1).run(episode=teacher_episode, agent_id='TEACHER')
    else:
        user_message = 'Entonces como consiguió relajar el problema humanitario de gaza del 2024?'
    print('User: ', user_message)
    print('==============================================================================')
    teacher_episode.log(channel='assistant', modality='text', content=user_message, agent_id='TEACHER')
    episode.log(channel='user', modality='text', content=user_message, agent_id='AGI1', emb=oaiemb._get_embedding(user_message))
    answer = LLMClientClass(model='gpt-4o', temperature=1).run(episode=episode, agent_id='AGI1')
    long_term_memory = get_neighbours(oaiemb.get_similarity(episode.history, 'emb', user_message + '->' + answer), 10, 20)
    short_term_memory = episode.history.tail(3)
    full_memory_episode.history = pd.concat([long_term_memory, short_term_memory], axis=0).drop_duplicates(['timestamp'])
    full_memory_episode.history = full_memory_episode.history.sort_values(by='timestamp', ascending=True)
    answer = LLMClientClass(model='gpt-4o', temperature=1).run(episode=full_memory_episode, agent_id='AGI1')
    episode.log(channel='assistant', modality='text', content=answer, agent_id='AGI1', emb=oaiemb._get_embedding(answer))
    teacher_episode.log(channel='user', modality='text', content=answer, agent_id='TEACHER')
    print('Assistant:', answer)
    print('==============================================================================')
    episode.history = episode.history[episode.history['steering'] == False]


