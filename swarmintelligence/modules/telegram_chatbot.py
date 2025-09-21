import asyncio
import logging
from typing import Callable, Any, Optional, List
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramChatbotClass:
    """
    Clase para crear un chatbot de Telegram con lógica de procesamiento personalizable.
    Incluye manejo automático de mensajes largos dividiéndolos en múltiples envíos.

    Attributes:
        token (str): Token del bot de Telegram
        chat_function (Callable): Función que procesará los mensajes
        application (Application): Aplicación de telegram
        max_message_length (int): Longitud máxima por mensaje (límite de Telegram: 4096)
    """

    def __init__(self, token: str, chat_function: Optional[Callable[[str, dict], str]] = None,
                 max_message_length: int = 4096):
        """
        Inicializa el chatbot.

        Args:
            token (str): Token del bot de Telegram obtenido de @BotFather
            chat_function (Callable): Función que procesará los mensajes.
                                    Debe recibir (mensaje: str, context: dict) y retornar str
            max_message_length (int): Longitud máxima por mensaje (por defecto 4096, límite de Telegram)
        """
        self.token = token
        self.chat_function = chat_function or self._default_chat_function
        self.application = None
        self.max_message_length = max_message_length
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

    def _split_message(self, text: str) -> List[str]:
        """
        Divide un mensaje largo en múltiples mensajes respetando el límite de caracteres.
        Intenta dividir por párrafos, luego por frases, y finalmente por caracteres.

        Args:
            text (str): Texto a dividir

        Returns:
            List[str]: Lista de mensajes divididos
        """
        if len(text) <= self.max_message_length:
            return [text]

        messages = []
        remaining_text = text

        while remaining_text:
            if len(remaining_text) <= self.max_message_length:
                messages.append(remaining_text)
                break

            # Intentar dividir por párrafos (doble salto de línea)
            chunk = remaining_text[:self.max_message_length]

            # Buscar el mejor punto de división
            split_points = [
                chunk.rfind('\n\n'),  # Párrafos
                chunk.rfind('\n'),  # Líneas
                chunk.rfind('. '),  # Frases
                chunk.rfind('? '),  # Preguntas
                chunk.rfind('! '),  # Exclamaciones
                chunk.rfind(', '),  # Comas
                chunk.rfind(' ')  # Espacios
            ]

            # Encontrar el mejor punto de división (el más lejano que no sea -1)
            split_point = -1
            for point in split_points:
                if point > split_point:
                    split_point = point

            if split_point == -1:
                # Si no hay buen punto de división, cortar por caracteres
                split_point = self.max_message_length - 3
                messages.append(chunk[:split_point] + '...')
                remaining_text = '...' + remaining_text[split_point:]
            else:
                # Ajustar el punto de división según el tipo de separador encontrado
                if remaining_text[split_point:split_point + 2] in ['\n\n', '. ', '? ', '! ', ', ']:
                    split_point += 2
                elif remaining_text[split_point] in ['\n', ' ']:
                    split_point += 1

                messages.append(remaining_text[:split_point].rstrip())
                remaining_text = remaining_text[split_point:].lstrip()

        return messages

    async def _send_message_parts(self, update: Update, text: str):
        """
        Envía un mensaje dividiéndolo en partes si es necesario.

        Args:
            update (Update): Objeto de actualización de Telegram
            text (str): Texto completo a enviar
        """
        message_parts = self._split_message(text)

        for i, part in enumerate(message_parts):
            try:
                if len(message_parts) > 1:
                    # Agregar indicador de parte si hay múltiples mensajes
                    part_indicator = f" ({i + 1}/{len(message_parts)})"
                    # Verificar que el indicador no cause que se supere el límite
                    if len(part) + len(part_indicator) <= self.max_message_length:
                        part += part_indicator

                await update.message.reply_text(part)

                # Pequeña pausa entre mensajes para evitar spam
                if i < len(message_parts) - 1:
                    await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error enviando parte {i + 1} del mensaje: {e}")
                await update.message.reply_text("Error enviando parte del mensaje.")

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
            "Usa /help para ver los comandos disponibles.\n\n"
            "💡 Puedo manejar respuestas largas dividiéndolas automáticamente en varios mensajes."
        )
        await self._send_message_parts(update, welcome_message)

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /help."""
        help_text = (
            "🤖 Comandos disponibles:\n\n"
            "/start - Iniciar conversación\n"
            "/help - Mostrar esta ayuda\n\n"
            "Simplemente envía cualquier mensaje y te responderé.\n\n"
            "📝 Características:\n"
            "• Manejo automático de respuestas largas\n"
            "• División inteligente de mensajes por párrafos, frases o palabras\n"
            "• Indicadores de partes cuando el mensaje se divide\n"
            f"• Límite por mensaje: {self.max_message_length} caracteres"
        )
        await self._send_message_parts(update, help_text)

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

            # Enviar respuesta (con división automática si es necesario)
            await self._send_message_parts(update, response)

            # Log de la interacción
            logger.info(f"Usuario {user.first_name} ({user.id}): {message_text}")
            logger.info(
                f"Bot respuesta ({len(response)} chars): {response[:100]}{'...' if len(response) > 100 else ''}")

        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            error_message = "Lo siento, ocurrió un error procesando tu mensaje. Inténtalo de nuevo."
            await self._send_message_parts(update, error_message)

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

