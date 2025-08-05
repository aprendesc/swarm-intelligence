
########################################################################################################################
"""Config v0"""
hypothesis = """Base search engine setup"""
version = '_v0'
preowned = True
active_config = {
            #COMPUTER USE
            'instructions': """Open google chrome. Look for the weather in Alpedrete (Madrid) using the web browser and give me the weather for the next sunday. Say OBJECTIVE ACCOMPLISHED when you finish.""",
            'model': "computer-use-preview",
            'continue_action': True,

            #CALL TO NOTION
            'recordings_path': "./data/curated/automations_app_call_recording/",

            #SMARTWATCH AUDIO TO NOTION
            'audio_path': 'G:/Mi unidad/utils/Easy Voice Recorder',
            'sw_notion_page': '23d2a599e98580d6b20dc30f999a1a2c',

            # YOUTUBE TO NOTION
            'yttn_video_url': 'https://www.youtube.com/watch?v=1uX0qHQfSMg',
            'yttn_notion_page': '2432a599e985804692b7d6982895a2b2',
            'yttn_summarize': True,
            'yttn_n_sections': 5,

            # SOURCE TO NOTION SUMMARY
            'source': 'Hola Mundo',
            'n_sections': 2,
            'summarizer_notion_page': '2432a599e985804692b7d6982895a2b2',

            # GENERATE_PODCAST
            'max_iter': 15,
            'podcast_folder_path': './data/processed/podcast_pipeline_stage',

            # LAUNCH PERSONAL
            'password': 's3cr3t!',
            'port': 5005,

            #LAUNCH PERSONAL SERVER NODE
            'node_ip': '127.0.0.1',
            'node_name': 'test_node',
            'node_method': lambda a, b: a + b,

            # CALL PERSONAL NODE
            'address_node_name': 'test_node',
            'node_call_payload': {'a': 1, 'b':2}
                }

########################################################################################################################