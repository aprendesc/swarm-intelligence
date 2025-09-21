import os

from eigenlib.utils.setup import Setup
Setup().init()

"""Basic agent call"""
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
if True:
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
