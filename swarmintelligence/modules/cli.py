from swarmintelligence.main import MainClass
from swarmintelligence.configs.test_config import test_config as config

class CLI:
    def __init__(self):
        print("""

██████╗░██████╗░░█████╗░░░░░░██╗███████╗░█████╗░████████╗  ░█████╗░██╗░░░░░██╗
██╔══██╗██╔══██╗██╔══██╗░░░░░██║██╔════╝██╔══██╗╚══██╔══╝  ██╔══██╗██║░░░░░██║
██████╔╝██████╔╝██║░░██║░░░░░██║█████╗░░██║░░╚═╝░░░██║░░░  ██║░░╚═╝██║░░░░░██║
██╔═══╝░██╔══██╗██║░░██║██╗░░██║██╔══╝░░██║░░██╗░░░██║░░░  ██║░░██╗██║░░░░░██║
██║░░░░░██║░░██║╚█████╔╝╚█████╔╝███████╗╚█████╔╝░░░██║░░░  ╚█████╔╝███████╗██║
╚═╝░░░░░╚═╝░░╚═╝░╚════╝░░╚════╝░╚══════╝░╚════╝░░░░╚═╝░░░  ░╚════╝░╚══════╝╚═╝
░╚════╝░╚══════╝╚═╝ 
                    """)
        self.main = MainClass(config)

    def run(self):
        while True:
            print("""
========================================================================================================================
""")

            # MENU
            menu_1 = """
1- CLI Chat
2- Tools Setup
3- Dataset Generation
4- Dataset Labeling
5- SFT
6- Eval
7- Predict
8- Launch Telegram Chatbot
9- Run frontend.

Select a method: """
            method = input(menu_1)

            print("""

█▀█ █▀▀ █▀ █▀█ █▀█ █▄░█ █▀ █▀▀
█▀▄ ██▄ ▄█ █▀▀ █▄█ █░▀█ ▄█ ██▄
========================================================================================================================
""")

            # TREE
            if method == '1':
                self._chat_interface(config)
            elif method == '2':
                self.main.tools_setup(config)
            elif method == '3':
                self.main.dataset_generation(config)
            elif method == '4':
                self.main.dataset_labeling(config)
            elif method == '5':
                self.main.train(config)
            elif method == '6':
                self.main.eval(config)
            elif method == '7':
                self.main.predict(config)
            elif method == '8':
                self.main.telegram_chatbot_run(config)
            elif method == '9':
                self.main.launch_front(config)

    def _chat_interface(self, config):
        history = []
        self.main.initialize(config)
        while True:
            config['user_message'] = input('User: ')
            config['history'] = history
            out_config = self.main.predict(config)
            print('Assistant: ', out_config['state_dict']['answer'])
            print("""
========================================================================================================================
                            """)


if __name__ == "__main__":
    CLI().run()
