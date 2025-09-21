import streamlit as st
import importlib
import pickle
import datetime
import os
from pathlib import Path
from eigenlib.utils.setup import Setup
from swarmintelligence.main import Main

Setup(verbose=True).init()


class SimpleChatInterface:
    def __init__(self):
        self.HISTORY_DIR = Path("chat_history")
        self.HISTORY_DIR.mkdir(exist_ok=True)

    def run(self):
        st.set_page_config(page_title="Chat Assistant", layout="wide")
        st.title("🤖 Chat Assistant")

        # Sidebar para configuración
        with st.sidebar:
            st.header("⚙️ Configuración")

            # Ruta de configuraciones
            config_path = st.text_input(
                "Ruta de configuraciones:",
                value=st.session_state.get('config_path', 'swarmintelligence/configs'),
                help="Ejemplo: /path/to/configs"
            )

            if config_path and Path(config_path).exists():
                # Obtener configuraciones disponibles
                configs = self._get_available_configs(config_path)
                if configs:
                    selected_config = st.selectbox(
                        "Seleccionar configuración:",
                        configs,
                        key="config_selector"
                    )

                    if st.button("🚀 Cargar Configuración"):
                        self._load_config(config_path, selected_config)
                        st.success(f"Configuración '{selected_config}' cargada")
                        st.rerun()
                else:
                    st.warning("No se encontraron configuraciones en la ruta")
            elif config_path:
                st.error("La ruta no existe")

            st.divider()

            # Gestión de chats
            st.header("💬 Chats")
            if st.button("➕ Nuevo Chat"):
                st.session_state.history = []
                st.session_state.current_chat_file = None
                st.rerun()

            # Cargar chats guardados
            saved_chats = self._get_saved_chats()
            if saved_chats:
                selected_chat = st.selectbox("Cargar chat:", saved_chats)
                col1, col2 = st.columns(2)
                if col1.button("📂 Cargar"):
                    st.session_state.history = self._load_chat_history(selected_chat)
                    st.session_state.current_chat_file = selected_chat
                    st.rerun()
                if col2.button("🗑️ Borrar"):
                    self._delete_chat_history(selected_chat)
                    if st.session_state.get('current_chat_file') == selected_chat:
                        st.session_state.history = []
                        st.session_state.current_chat_file = None
                    st.rerun()

            st.divider()

            # Subir imagen
            st.header("🖼️ Imagen")
            image_file = st.file_uploader(
                "Subir imagen:",
                type=["png", "jpg", "jpeg", "gif"]
            )
            image_url = st.text_input("O URL de imagen:")

        # Inicializar sesión
        if 'history' not in st.session_state:
            st.session_state.history = []

        if 'main_class' not in st.session_state and 'config' in st.session_state:
            with st.spinner("Inicializando asistente..."):
                try:
                    st.session_state.main_class = Main()
                    updated_cfg = st.session_state.main_class.initialize(
                        st.session_state.config['initialize'].copy()
                    )
                    st.session_state.history = updated_cfg.get('history', [])
                    st.toast("✅ Asistente inicializado")
                except Exception as e:
                    st.error(f"Error en inicialización: {e}")

        # Área de chat
        if 'config' not in st.session_state:
            st.info("👈 Selecciona una configuración en el panel lateral para comenzar")
        else:
            # Mostrar historial
            chat_container = st.container(height=1600)
            with chat_container:
                for message in st.session_state.history:
                    role = message.get("role", "user")
                    content = message.get("content", "")
                    modality = message.get("modality", None)
                    avatar = "🧑‍💻" if role == "user" else "🤖"

                    with st.chat_message(role, avatar=avatar):
                        if modality == 'img':
                            st.image(content, width=250)
                        elif modality == 'tool_call' or role == 'tool':
                            st.json(content, expanded=False)
                        else:
                            self._display_message(content)

            # Input del usuario
            if prompt := st.chat_input("Escribe tu mensaje aquí..."):
                if 'main_class' not in st.session_state:
                    st.error("⚠️ El asistente no está inicializado")
                    return

                # Procesar imagen si existe
                img_src = None
                if image_file is not None:
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{ts}_{image_file.name}"
                    save_path = self.HISTORY_DIR / filename
                    with open(save_path, "wb") as f:
                        f.write(image_file.getbuffer())
                    img_src = str(save_path)
                elif image_url and image_url.strip():
                    img_src = image_url.strip()

                # Enviar mensaje al asistente
                call_cfg = st.session_state.config['predict'].copy()
                call_cfg.update({
                    'history': st.session_state.history,
                    'user_message': prompt,
                    'img': img_src
                })

                with st.spinner("🤔 Pensando..."):
                    try:
                        updated = st.session_state.main_class.predict(call_cfg)
                        if updated:
                            st.session_state.history = updated.get('history', [])

                            # Guardar chat automáticamente
                            if st.session_state.get('current_chat_file') is None:
                                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                st.session_state.current_chat_file = f"chat_{ts}.pkl"

                            self._save_chat_history(
                                st.session_state.history,
                                st.session_state.current_chat_file
                            )
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error procesando mensaje: {e}")

    def _get_available_configs(self, config_path):
        """Obtiene las configuraciones disponibles en la ruta especificada."""
        try:
            configs = []
            for file in Path(config_path).iterdir():
                if file.is_file() and 'config' in file.name.lower() and file.suffix == '.py':
                    configs.append(file.stem)
            return sorted(configs)
        except Exception:
            return []

    def _load_config(self, config_path, config_name):
        """Carga la configuración seleccionada."""
        try:
            # Agregar la ruta al sys.path temporalmente
            import sys
            if str(config_path) not in sys.path:
                sys.path.insert(0, str(config_path))

            # Importar el módulo de configuración
            module = importlib.import_module(config_name)
            cfg_object = getattr(module, "Config")()

            st.session_state.config = {
                'initialize': cfg_object.initialize(),
                'predict': cfg_object.predict(),
            }
            st.session_state.config_path = config_path

            # Limpiar instancia anterior si existe
            if 'main_class' in st.session_state:
                del st.session_state.main_class

        except Exception as e:
            st.error(f"Error cargando configuración: {e}")

    def _get_saved_chats(self):
        """Obtiene la lista de chats guardados."""
        return sorted([f.name for f in self.HISTORY_DIR.glob("*.pkl")], reverse=True)

    def _save_chat_history(self, history, filename):
        """Guarda el historial del chat."""
        with open(self.HISTORY_DIR / filename, "wb") as f:
            pickle.dump(history, f)

    def _load_chat_history(self, filename):
        """Carga el historial del chat."""
        try:
            with open(self.HISTORY_DIR / filename, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            st.error(f"Error cargando chat: {e}")
            return []

    def _delete_chat_history(self, filename):
        """Elimina un chat guardado."""
        try:
            (self.HISTORY_DIR / filename).unlink()
            st.success(f"Chat '{filename}' eliminado")
        except Exception as e:
            st.error(f"Error eliminando chat: {e}")

    def _display_message(self, text):
        """Muestra un mensaje en una caja escalable."""
        text_length = len(str(text))
        min_height = 50
        max_height = 700
        max_text_length = 2000

        if text_length < max_text_length:
            height = int(min_height + (max_height - min_height) * (text_length / max_text_length))
        else:
            height = max_height

        with st.container(height=height):
            st.text(text)


if __name__ == '__main__':
    SimpleChatInterface().run()