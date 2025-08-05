from eigenlib.LLM.episode import EpisodeClass
from eigenlib.LLM.oai_llm import OAILLMClientClass

class SourceSummarizationClass:
            def __init__(self):
                pass

            def run(self, source, n_sections=15, max_len=350000, overlap=25000, temperature=1, model='gpt-4.1'):
                source = source.replace('\n\n', '')
                source_chunks = []
                start = 0
                text_length = len(source)

                while start < text_length:
                    end = start + max_len
                    chunk = source[start:end]
                    source_chunks.append(chunk)
                    start = end - overlap

                episode = EpisodeClass()
                n_subsections = int(n_sections/len(source_chunks))
                counter = 0
                for c in source_chunks:
                    A_prompt = f"""
# Instrucciones:
* Vas a ser entrevistado sobre la siguiente fuente: "{c}"
* Se corresponde con la parte {str(counter)} de {str(len(source_chunks))} de la fuente.
* Generarás las secciones del resumen de manera cronológica.
* Resumirás con mayor o menor grado de compresión en función del grado de sumarización solicitado. (Más secciones = Menos resumen).
* A la hora de resumir, te centrarás siempre en preservar el contenido de mayor valor informativo, puntos clave y elementos centrales.
* Resume en formato markdown y preservando el estilo del autor, como si fuera el mismo autor el que resume.
* Ahorrate conectores como "Claro, aqui tienes tu resumen..." tu respuesta debe contener directamente el resumen.
"""
                    S_prompt = f"""Genera un indice de las {n_subsections} secciones de las que se va a componer el resumen para cubrir el contenido. 
Responde simplemente con los puntos a tratar numerados. Tu respuesta debe contener solo los puntos."""

                    episode.log(channel='system', modality='text', content=A_prompt, agent_id='S')
                    episode.log(channel='system', modality='text', content=S_prompt, agent_id='S')
                    S_message = OAILLMClientClass(model=model, temperature=temperature).run(episode, agent_id='S', use_steering=True, tool_choice='none')
                    episode.log(channel='system', modality='text', content=A_prompt, agent_id='A')
                    episode.log(channel='system', modality='text', content='Puntos del resumen:\n' + S_message, agent_id='A')
                    episode.history = episode.history[episode.history['channel'] != 'steering']
                    print('PLAN:', S_message)
                    print('--------------------------------------')
                    for i in range(n_subsections):
                        episode.log(channel='user', modality='text', content=f'Resume el bloque número {str(i+1)} de {str(n_subsections)}', agent_id='A')
                        A_message = OAILLMClientClass(model=model, temperature=temperature).run(episode, agent_id='A', use_steering=True, tool_choice='none')
                        episode.log(channel='assistant', modality='text', content=A_message, agent_id='A')
                        print('SUMMARY: ', A_message)
                    episode.history = episode.history[episode.history['channel'] != 'system']
                    counter += 1

                history = episode.history
                history = history[history['agent_id'] == 'A']
                summary = history[history['channel'] == 'assistant']['content'].iloc[1:].sum()
                summary = summary.replace('```markdown', '').replace('```', '')

                return summary