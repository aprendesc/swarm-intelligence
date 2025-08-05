from eigenlib.utils.project_setup import ProjectSetupClass
ProjectSetupClass(project_name='swarmintelligence', app_name='automations')

class MainClass():
    def __init__(self, config):
        pass

    def computer_use_automation(self, config):
        from eigenlib.LLM.computer_use_tools import ComputerUseClass
        ################################################################################################################
        continue_action = config['continue_action']
        instructions = config['instructions']
        model = config['model']
        ################################################################################################################
        CUA = ComputerUseClass()
        CUA.run(continue_action, instructions, model)
        return config

    def standby(self, config):
        from swarmintelligence.automations_app.modules.standby import StandbyClass
        ################################################################################################################
        monitor = StandbyClass(timeout=45)
        monitor.run()

    def call_to_notion(self, config):
        from swarmintelligence.automations_app.modules.call_recording_pipeline import CallRecordingPipelineClass
        ################################################################################################################
        recordings_dir = config['recordings_path']
        ################################################################################################################
        CallRecordingPipelineClass().run()
        return config

    def listen_smartwatch_notes(self, config):
        from eigenlib.audio.oai_whisper_stt import OAIWhisperSTTClass
        from eigenlib.utils.notion_utils import NotionUtilsClass
        import os
        import time

        ################################################################################################################
        audio_path = config['audio_path']
        notion_page = config['sw_notion_page']
        ################################################################################################################

        whisper_model = OAIWhisperSTTClass()
        NU = NotionUtilsClass()

        print(f"📡 Monitoreando carpeta: {audio_path}")
        processed_files = set()

        while True:
            try:
                current_files = set(os.listdir(audio_path))
                new_files = current_files - processed_files

                for f in new_files:
                    file_path = os.path.join(audio_path, f)

                    if os.path.isfile(file_path):
                        print(f"🎙️  Nuevo archivo detectado: {f}")
                        transcription = whisper_model.run(file_path, engine='cloud')
                        NU.write(page_id=notion_page, texto='* ' + transcription)
                        os.remove(file_path)
                        print(f"✅ Procesado y eliminado: {f}")
                        time.sleep(2)  # Pequeña pausa tras el procesamiento

                processed_files = current_files
                time.sleep(5)  # Esperar antes de la próxima comprobación

            except Exception as e:
                print(f"❌ Error durante el procesamiento: {e}")
                time.sleep(5)

    def youtube_to_notion(self, config):
        import tempfile
        from eigenlib.utils.youtube_utils import YoutubeUtilsClass
        from eigenlib.audio.oai_whisper_stt import OAIWhisperSTTClass
        from eigenlib.utils.notion_utils import NotionUtilsClass
        from swarmintelligence.automations_app.modules.automatic_summarizer import SourceSummarizationClass
        ################################################################################################################
        video_url = config['yttn_video_url']
        notion_page = config['yttn_notion_page']
        summarize = config['yttn_summarize']
        n_sections = config['yttn_n_sections']
        ################################################################################################################
        youtube_utils = YoutubeUtilsClass(quiet=False)
        whisper_model = OAIWhisperSTTClass()
        with tempfile.TemporaryDirectory() as tmpdir:
            result_path = youtube_utils.download_audio(video_url=video_url, output_dir=tmpdir, filename='temp_audio', compress=True, compression_level='medium')
            transcription = whisper_model.run(result_path, engine='cloud')
        print('Transcription completed')
        if summarize:
            transcription = SourceSummarizationClass().run(transcription, n_sections=int(n_sections))
            print('Summarization completed')
        NU = NotionUtilsClass()
        NU.write(page_id=notion_page, texto='* ' + transcription)
        return config

    def source_to_notion_summary(self):
        from swarmintelligence.automations_app.modules.automatic_summarizer import SourceSummarizationClass
        from eigenlib.utils.notion_utils import NotionUtilsClass
        ################################################################################################################
        source = config['source']
        notion_page = config['summarizer_notion_page']
        ################################################################################################################
        summary = SourceSummarizationClass().run(source, n_sections=2)
        NU = NotionUtilsClass()
        NU.write(page_id=notion_page, texto='* ' + summary)

    def podcast_generation(self, config):
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
        from eigenlib.LLM.sources_parser import SourcesParserClass
        from eigenlib.LLM.episode import EpisodeClass
        from eigenlib.LLM.oai_llm import OAILLMClientClass
        from eigenlib.audio.OAI_TTS import OAITTSModelClass
        from eigenlib.image.dalle_model import DalleModelClass
        import os
        import pandas as pd
        import numpy as np
        import soundfile as sf
        import time
        ################################################################################################################
        max_iter = config['max_iter']
        podcast_path = config['podcast_folder_path']
        ################################################################################################################
        SP = SourcesParserClass()
        path = 'C:/Users/AlejandroPrendesCabo/Desktop/proyectos/swarm-intelligence-project/data/raw/source_papers'
        ########################################################################################################################
        files = os.listdir(path)
        print(pd.Series(files))
        selection = int(input('Seleccione el paper a generar: '))
        input_file = os.path.join(path, files[selection])
        path = input_file
        name = input_file.replace('.pdf', '').split('\\')[-1]

        source = SP.run(path)
        podcast_path = os.path.join(podcast_path, name)
        os.makedirs(podcast_path, exist_ok=True)
        Q_system_prompt = f"""Fuente de información que debes emplear:\n'{source}
Eres un entrevistador del podcast Aligned Humans llamado Light y tu objetivo es ir manteniendo un dialogo. Realiza preguntas cortas en orden, inteligentes, avanzadas, con mucho sentido haciendo al entrevistado sentirse cómodo.
El podcast constará en total de {str(max_iter)} preguntas, así que estructura tus preguntas de forma adecuada para cubrir con ese nivel de detalle asumiento que el oyente ya tiene un alto conocimiento de IA.
"""
        A_system_prompt = f"""Fuente de información que debes emplear para responder en el podcast: \n'{source}
Eres Signal una experta que esta realizando un podcast y tu objetivo es ir manteniendo una conversación técnica pero muy amena sobre las preguntas que el entrevistador llamado (Light) te va a ir haciendo usando el conocimiento de la fuente. Tus respuestas deben ser breves y dinámicas pero cargadas de contenido y de insight, sin miedo a sonar técnica. Asume que oyente ya tiene conocimientos avanzados de IA. Recuerda ser breve y al grano.
    """

        episode = EpisodeClass()
        episode.log(channel='system', modality='text', content=Q_system_prompt, agent_id='Q')
        episode.log(channel='system', modality='text', content=A_system_prompt, agent_id='A')

        A_message = """Genera una introducción al podcast, por ejemplo 'Bienvenidos a aligned humans, el espacio de donde sincronizamos al humano con la realidad de la inteligencia artificial. Prepara tus conexiones neuronales porque comienza el viaje. Hoy tenemos con nosotros a... (presentación breve de la invitada llamada Signal experta en la fuente que es quien entrevistarás, presentala un poco.)'"""
        for i in range(0, max_iter):
            print(i)
            start_time = time.time()

            episode.log(channel='system', modality='text', content=f'Haz la pregunta número {str(i)}', agent_id='Q')
            episode.log(channel='user', modality='text', content=A_message, agent_id='Q')
            Q_message = OAILLMClientClass(model='gpt-4.1', temperature=1).run(episode, agent_id='Q')
            episode.log(channel='assistant', modality='text', content=Q_message, agent_id='Q')

            OAITTSModelClass(voice='echo').run(Q_message.encode('utf-8').decode('utf-8'), podcast_path + f'/turno_{str(i)}_int.mp3')

            episode.log(channel='user', modality='text', content=Q_message, agent_id='A')
            A_message = OAILLMClientClass(model='gpt-4.1', temperature=1).run(episode, agent_id='A')
            episode.log(channel='assistant', modality='text', content=A_message, agent_id='A')
            OAITTSModelClass(voice='nova').run(A_message.encode('utf-8').decode('utf-8'), podcast_path + f'/turno_{str(i)}_guest.mp3')

            if i > 0:
                elapsed_time = time.time() - start_time
                remaining_time = 22 - elapsed_time
                if remaining_time > 0:
                    time.sleep(remaining_time)

                img_input_prompt = """f'Genera un prompt para generar una imagen a partir del mensaje del usuario. Responde unicamente con las keywords en inglés para generar una imagen visualmente impactante y relacionadas con el texto.'"""
                episode.log(channel='user', modality='text', content=img_input_prompt, agent_id='A')
                img_prompt = OAILLMClientClass(model='gpt-4.1', temperature=1).run(episode, agent_id='A')
                image = DalleModelClass().predict(img_prompt)
                image.convert('RGB').save(podcast_path + '/' + f'image_{str(i)}.jpeg', format='JPEG')
                time.sleep(30)

        history = episode.history
        history = history[history['agent_id'] == 'A']
        messages_df = history[history['channel'] != 'system']

        # SAVE TEXT
        text_podcast = (messages_df['content'] + '\n').sum()
        with open(podcast_path + '/final_script.txt', "w", encoding="utf-8") as archivo:
            archivo.write(text_podcast)

        silencio = np.zeros(int(24000 * 1.0), dtype=np.float32)  # 1 segundo de silencio
        combinado = []

        for i in range(0, max_iter):
            audio, sr = sf.read(podcast_path + f'/turno_{str(i)}_int.mp3', dtype='float32')
            combinado.append(audio)
            combinado.append(silencio)
            audio, sr = sf.read(podcast_path + f'/turno_{str(i)}_guest.mp3', dtype='float32')
            combinado.append(audio)
            combinado.append(silencio)

        audio_final = np.concatenate(combinado)
        wav_path = podcast_path + '/final_audio.wav'
        sf.write(wav_path, audio_final, 24000)

        #VIDEO GENERATION
        audio = AudioFileClip(podcast_path + '/final_audio.wav')
        spec = []
        delta = audio.duration / (max_iter - 2)
        for i in range(2, max_iter):
            spec.append((podcast_path + f'/image_{str(i)}.jpeg', delta * (i - 2), delta * (i + 1 - 2)))

        output_path = podcast_path + '/' + "final_video.mp4"
        fps = 24

        clips = []
        for ruta, t0, t1 in spec:
            dur = t1 - t0
            clip = ImageClip(ruta).set_duration(dur)
            clips.append(clip)

        video = concatenate_videoclips(clips, method="compose")
        if video.duration > audio.duration:
            video = video.subclip(0, audio.duration)
        else:
            video = video.set_duration(audio.duration)

        video = video.set_audio(audio)
        video.write_videofile(output_path, fps=fps, codec="libx264", audio_codec="aac")
        return config

    """Personal server"""
    def launch_personal_server(self, config):
        from eigenlib.utils.general_purpose_net import GeneralPurposeNetClass
        ################################################################################################################
        port = config['port']
        password = config['password']
        ################################################################################################################
        server = GeneralPurposeNetClass()
        server.start_server(port=port, password=password)
        return config

    def launch_personal_server_node(self, config):
        from eigenlib.utils.general_purpose_net import GeneralPurposeNetClass
        ################################################################################################################
        node_ip = config['node_ip']
        port = config['port']
        node_name = config['node_name']
        node_method = config['node_method']
        password = config['password']
        ################################################################################################################
        nodeA = GeneralPurposeNetClass()
        nodeA.start_node(node_name=node_name, server_address=node_ip+":"+str(port), password=password, method=node_method)
        return config

    def call_personal_server_node(self, config):
        from eigenlib.utils.general_purpose_net import GeneralPurposeNetClass
        ################################################################################################################
        node_ip = config['node_ip']
        port = config['port']
        address_node_name = config['address_node_name']
        node_call_payload = config['node_call_payload']
        password = config['password']
        ################################################################################################################
        client_node = GeneralPurposeNetClass()
        client_node.start_node(node_name="client_node", server_address=node_ip+":"+str(port), password=password, method=lambda a, b: a + b)
        config['result'] = client_node.call_node(address_node_name, node_call_payload)
        client_node.stop()
        return config

if __name__ == '__main__':
    from swarmintelligence.automations_app.config import active_config as config
    main = MainClass(config)
    #main.computer_use_automation(config)
    main.standby(config)
    #main.call_to_notion(config)
    #main.listen_smartwatch_notes(config)
    #main.youtube_to_notion(config)
    #main.source_to_notion_summary(config)
    #main.generate_podcast(config)
    #main.launch_personal_server(config)
    #main.launch_personal_server_node(config)
    #main.call_personal_server_node(config)
