import os
import streamlit as st
import importlib
import pickle
import json
from pathlib import Path
from eigenlib.genai.memory import Memory
import pandas as pd
from eigenlib.utils.setup import Setup

Setup(verbose=True).init()

class SimpleChatInterface:
    def __init__(self):
        # Directorio por defecto si no hay configuración
        self.DEFAULT_HISTORY_DIR = Path("swarmintelligence/modules")

    def run(self):
        st.set_page_config(page_title="Chat Assistant", layout="wide")
        st.title("Chat Assistant")

        # Inicializar estados de sesión para edición
        if 'editing_index' not in st.session_state:
            st.session_state.editing_index = None
        if 'edit_text' not in st.session_state:
            st.session_state.edit_text = ""

        # Sidebar para configuración
        with st.sidebar:
            st.header("⚙️ Configuración")
            config_path = st.text_input("Ruta de configuraciones:", value=st.session_state.get('config_path', os.environ['package_name'] + '/modules'), help="Ejemplo: /path/to/configs")

            if config_path and Path(config_path).exists():
                # Obtener configuraciones disponibles
                configs = self._get_available_configs(config_path)
                if configs:
                    selected_config = st.selectbox("Seleccionar configuración:", configs, key="config_selector")
                    if st.button("🚀 Initialize"):
                        module = importlib.import_module((config_path + '/' + selected_config).replace('/', '.'))
                        agent = getattr(module, "SwarmIntelligenceAgent")()
                        st.success(f"Agente seleccionado")
                        memory = agent.initialize()
                        st.session_state.memory_file = agent.memory_file
                        st.session_state.agent = agent
                        try:
                            loaded_history = pickle.load(open(agent.memory_file, "rb"))
                            st.session_state.history = loaded_history
                        except:
                            st.session_state.history = memory.history.to_dict(orient='records')
                            os.makedirs(os.path.dirname(st.session_state.memory_file), exist_ok=True)
                            pickle.dump(st.session_state.history, open(st.session_state.memory_file, "wb"))
                        st.rerun()
                else:
                    st.warning("No se encontraron configuraciones en la ruta")
            elif config_path:
                st.error("La ruta no existe")
            st.divider()

            #json_str = st.text_area("Config", value=json.dumps(st.session_state.config.interface, indent=2), height=200)
            st.header("⚙️ Memory Viewer")
            agent_name = st.session_state.agent.id
            sel_channel = st.multiselect("Selected channel:", [agent_name], default=[agent_name])
            sel_roles = st.multiselect("Selected roles:", ['user', 'assistant', 'system', 'tool'], default=['user', 'assistant', 'tool'])

            # Subir imagen
            st.header("🖼️ Imagen")
            image_file = st.file_uploader("Subir imagen:", type=["png", "jpg", "jpeg", "gif"])
            image_url = st.text_input("O URL de imagen:")

            if st.session_state.editing_index is not None:
                if st.button("❌ Cancelar Edición"):
                    st.session_state.editing_index = None
                    st.session_state.edit_text = ""
                    st.rerun()
                st.info(f"Editando mensaje #{st.session_state.editing_index}")

        # Área de chat
        if 'agent' not in st.session_state:
            st.info("👈 Selecciona una configuración en el panel lateral para comenzar")
        else:
            # Mostrar interfaz de edición si está activa
            if st.session_state.editing_index is not None:
                self._show_edit_interface()

            chat_container = st.container(height=1600)
            with chat_container:
                for idx, message in enumerate(st.session_state.history):
                    if (message.get("channel") in sel_channel and message.get("role") in sel_roles):
                        role = message.get("role", "user")
                        content = message.get("content", "")
                        modality = message.get("modality", None)
                        avatar = "🧑‍💻" if role == "user" else "🤖"

                        with st.chat_message(role, avatar=avatar):
                            # Crear columnas para contenido y botón de editar
                            col1, col2 = st.columns([10, 1])

                            with col1:
                                if modality == 'img':
                                    st.image(content, width=250)
                                elif modality == 'tool_call':
                                    st.json(content, expanded=False)
                                elif role == 'tool':
                                    st.json(content, expanded=False)
                                else:
                                    self._display_message(content)

                            with col2:
                                # Solo mostrar botón de editar para mensajes de texto que no son de herramientas
                                if (modality not in ['img', 'tool_call'] and role != 'tool' and
                                        st.session_state.editing_index != idx):
                                    if st.button("✏️", key=f"edit_{idx}", help="Editar mensaje"):
                                        st.session_state.editing_index = idx
                                        st.session_state.edit_text = str(content)
                                        st.rerun()

            # Input del usuario (solo si no está editando)
            if st.session_state.editing_index is None:
                if prompt := st.chat_input("Escribe tu mensaje aquí..."):
                    if 'agent' not in st.session_state:
                        st.error("⚠️ El asistente no está inicializado")
                        return


                    with st.spinner("🤔 Pensando..."):
                        try:
                            memory = Memory()
                            memory.history = pd.DataFrame(st.session_state.history)
                            memory, answer = st.session_state.agent.call(**{'memory': memory, 'user_message': prompt, 'img': None})
                            if answer:
                                st.session_state.history = memory.history.to_dict(orient='records')
                                pickle.dump(st.session_state.history, open(st.session_state.memory_file, "wb"))
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error procesando mensaje: {e}")

    def _show_edit_interface(self):
        """Muestra la interfaz de edición de mensajes."""
        st.header("✏️ Editando Mensaje")

        # Área de texto para editar
        edited_text = st.text_area(
            "Edita el contenido del mensaje:",
            value=st.session_state.edit_text,
            height=150,
            key="edit_textarea"
        )

        # Botones de acción
        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Guardar Cambios", type="primary"):
                # Actualizar el mensaje en el historial
                st.session_state.history[st.session_state.editing_index]["content"] = edited_text

                # Guardar en archivo
                pickle.dump(st.session_state.history, open(st.session_state.memory_file, "wb"))

                # Limpiar estado de edición
                st.session_state.editing_index = None
                st.session_state.edit_text = ""

                st.success("✅ Mensaje actualizado correctamente")
                st.rerun()

        with col2:
            if st.button("🗑️ Eliminar Mensaje"):
                # Eliminar mensaje del historial
                del st.session_state.history[st.session_state.editing_index]

                # Guardar en archivo
                pickle.dump(st.session_state.history, open(st.session_state.memory_file, "wb"))

                # Limpiar estado de edición
                st.session_state.editing_index = None
                st.session_state.edit_text = ""

                st.success("🗑️ Mensaje eliminado correctamente")
                st.rerun()

    def _get_available_configs(self, config_path):
        """Obtiene las configuraciones disponibles en la ruta especificada."""
        try:
            configs = []
            for file in Path(config_path).iterdir():
                if file.is_file() and 'agent' in file.name.lower() and file.suffix == '.py':
                    configs.append(file.stem)
            return sorted(configs)
        except Exception:
            return []

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
    import sys
    import subprocess
    from streamlit.runtime.scriptrunner import get_script_run_ctx

    # La condición get_script_run_ctx() es la forma fiable de saber si se ejecuta con Streamlit
    if get_script_run_ctx():
        # Si es True, ya estamos dentro de Streamlit, así que dibujamos la app
        SimpleChatInterface().run()
    else:
        # Si es False, significa que se ejecutó con 'python <nombre_script>.py'
        # Así que lanzamos Streamlit usando un subproceso
        # Usamos sys.argv[0] que es el nombre del script actual
        try:
            subprocess.run(["streamlit", "run", sys.argv[0]], check=True)
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"Error al intentar lanzar Streamlit: {e}")
            print("Asegúrate de que Streamlit esté instalado y en el PATH del sistema.")
            print("Puedes instalarlo con: pip install streamlit")