import asyncio
import logging
from typing import Callable, Any, Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramChatbotClass:
    """
    Clase para crear un chatbot de Telegram con lógica de procesamiento personalizable.

    Attributes:
        token (str): Token del bot de Telegram
        chat_function (Callable): Función que procesará los mensajes
        application (Application): Aplicación de telegram
    """

    def __init__(self, token: str, chat_function: Optional[Callable[[str, dict], str]] = None):
        """
        Inicializa el chatbot.

        Args:
            token (str): Token del bot de Telegram obtenido de @BotFather
            chat_function (Callable): Función que procesará los mensajes.
                                    Debe recibir (mensaje: str, context: dict) y retornar str
        """
        self.token = token
        self.chat_function = chat_function or self._default_chat_function
        self.application = None
        self._setup_application()

    def _setup_application(self):
        """Configura la aplicación de Telegram."""
        self.application = Application.builder().token(self.token).build()

        # Manejadores
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

    def set_chat_function(self, chat_function: Callable[[str, dict], str]):
        """
        Establece o cambia la función de procesamiento de chat.

        Args:
            chat_function (Callable): Función que procesará los mensajes.
                                    Debe recibir (mensaje: str, context: dict) y retornar str
        """
        self.chat_function = chat_function

    def _default_chat_function(self, message: str, context: dict) -> str:
        """
        Función de chat por defecto que simplemente hace echo del mensaje.

        Args:
            message (str): Mensaje recibido
            context (dict): Contexto del mensaje (usuario, chat_id, etc.)

        Returns:
            str: Respuesta del bot
        """
        return f"Echo: {message}"

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /start."""
        user = update.effective_user
        welcome_message = (
            f"¡Hola {user.first_name}! 👋\n"
            "Soy tu chatbot personal. Envíame cualquier mensaje y te responderé.\n"
            "Usa /help para ver los comandos disponibles."
        )
        await update.message.reply_text(welcome_message)

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /help."""
        help_text = (
            "🤖 Comandos disponibles:\n\n"
            "/start - Iniciar conversación\n"
            "/help - Mostrar esta ayuda\n\n"
            "Simplemente envía cualquier mensaje y te responderé."
        )
        await update.message.reply_text(help_text)

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja los mensajes de texto recibidos.

        Args:
            update (Update): Objeto de actualización de Telegram
            context (ContextTypes.DEFAULT_TYPE): Contexto de la conversación
        """
        try:
            # Extraer información del mensaje
            message_text = update.message.text
            user = update.effective_user
            chat_id = update.effective_chat.id

            # Crear contexto para la función de chat
            chat_context = {
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'chat_id': chat_id,
                'message_id': update.message.message_id,
                'date': update.message.date,
                'chat_type': update.effective_chat.type
            }

            # Procesar el mensaje con la función de chat personalizada
            response = self.chat_function(message_text, chat_context)

            # Enviar respuesta
            await update.message.reply_text(response)

            # Log de la interacción
            logger.info(f"Usuario {user.first_name} ({user.id}): {message_text}")
            logger.info(f"Bot respuesta: {response}")

        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            error_message = "Lo siento, ocurrió un error procesando tu mensaje. Inténtalo de nuevo."
            await update.message.reply_text(error_message)

    def run(self, polling: bool = True):
        """
        Método principal que inicia el servidor del bot.

        Args:
            polling (bool): Si usar polling (True) o webhooks (False)
        """
        try:
            logger.info("🚀 Iniciando el chatbot de Telegram...")

            if polling:
                # Usar polling para desarrollo local
                logger.info("📡 Usando polling para recibir mensajes...")
                self.application.run_polling(
                    allowed_updates=Update.ALL_TYPES,
                    drop_pending_updates=True
                )
            else:
                # Para usar webhooks (producción)
                logger.info("🌐 Configurado para webhooks...")
                # Nota: Necesitarías configurar webhooks según tu servidor
                raise NotImplementedError("Webhooks no implementados en este ejemplo")

        except KeyboardInterrupt:
            logger.info("❌ Bot detenido por el usuario")
        except Exception as e:
            logger.error(f"💥 Error ejecutando el bot: {e}")
            raise

    def stop(self):
        """Detiene el bot de forma segura."""
        if self.application:
            logger.info("🛑 Deteniendo el bot...")
            self.application.stop()
