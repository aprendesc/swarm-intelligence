import os
import importlib
import streamlit as st
import pickle
import datetime
import inspect
from pathlib import Path
from eigenlib.utils.data_utils import DataUtilsClass
from swarmintelligence.main import MainClass
if True:
    import sys
    import os
    from dotenv import load_dotenv
    ####################################################################################################################
    project_folder = 'swarm-intelligence'
    base_path = f'C:/Users/{os.environ["USERNAME"]}/Desktop/proyectos'
    ####################################################################################################################
    load_dotenv()
    os.getcwd()
    sys.path.extend([
        os.path.join(base_path, 'swarm-ml'),
        os.path.join(base_path, 'swarm-intelligence'),
        os.path.join(base_path, 'swarm-automations'),
        os.path.join(base_path, 'swarm-compute'),
        os.path.join(base_path, 'eigenlib')
    ])
    os.environ['PROJECT_NAME'] = project_folder.replace('-', '')
    os.environ['PROJECT_FOLDER'] = project_folder
    os.chdir(os.path.join(base_path, project_folder))

class FrontEndClass:
    def __init__(self):
        pass

    def run(self):

        # --- CONSTANTES Y RUTAS ---
        RAW_DATA_PATH    = Path(os.environ['RAW_DATA_PATH'])
        CURATED_DATA_PATH= Path(os.environ['CURATED_DATA_PATH'])
        HISTORY_DIR      = Path(os.environ['PROCESSED_DATA_PATH']) / "personal_assistant_chat_history"
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)

        def get_available_configs():
            """Revisa el directorio ./<PROJECT_NAME>/configs y devuelve un diccionario con nombres de archivo y rutas."""
            base_path = f'./{os.environ["PROJECT_NAME"]}/configs'
            configs = [c for c in os.listdir(base_path) if 'config' in c.lower()]
            return configs

        def get_all_raw_files(directory: Path):
            if not directory.exists(): return []
            return [f.name for f in directory.iterdir() if f.is_file()]

        def get_dataset_directories(directory: Path, identifier: str):
            if not directory.exists(): return []
            return sorted([f.name for f in directory.iterdir()
                           if f.is_dir() and identifier.lower() in f.name.lower()],
                          reverse=True)

        def get_saved_chats():
            return sorted([f.name for f in HISTORY_DIR.glob("*.pkl")], reverse=True)

        def save_chat_history(history, filename):
            with open(HISTORY_DIR / filename, "wb") as f:
                pickle.dump(history, f)

        def load_chat_history(filename):
            try:
                with open(HISTORY_DIR / filename, "rb") as f:
                    return pickle.load(f)
            except (FileNotFoundError, pickle.UnpicklingError):
                st.error(f"No se pudo cargar el chat '{filename}'.")
                return []

        def delete_chat_history(filename):
            try:
                (HISTORY_DIR / filename).unlink()
                st.success(f"Chat '{filename}' eliminado.")
            except FileNotFoundError:
                st.error(f"El archivo '{filename}' no se encontró para eliminar.")

        def display_message(text):
            """Muestra un mensaje de texto dentro de una caja escalable."""
            MIN_HEIGHT = 50
            MAX_HEIGHT = 700
            MAX_TEXT_LENGTH = 3200
            text_length = len(str(text))
            if text_length < MAX_TEXT_LENGTH:
                height = int(MIN_HEIGHT + (MAX_HEIGHT - MIN_HEIGHT) *
                             2 * (text_length / MAX_TEXT_LENGTH))
            else:
                height = MAX_HEIGHT
            with st.container(height=height):
                st.text(text)

            from eigenlib.utils.alert_utils import AlertsUtils
            import os
            AlertsUtils().run("test_message", bot_token=os.environ["TELEGRAM_BOT_TOKEN_2"], bot_chatID=int(os.environ["TELEGRAM_CHAT_ID_2"]))

        def render_dataset_viewer():
            """Muestra la interfaz de visualización y edición de datasets."""
            info = st.session_state.viewing_dataset_info
            st.title(f"👁️ Visor de Dataset: {info['name']}")
            if st.button("⬅️ Volver al Chat"):
                st.session_state.view_mode = 'chat'
                st.session_state.viewing_dataset_info = None
                st.rerun()

            st.caption(f"Estás viendo y editando el dataset '{info['name']}' en `{CURATED_DATA_PATH}`.")
            try:
                with st.spinner("Cargando dataset..."):
                    du = DataUtilsClass()
                    try:
                        df = du.load_dataset(path=str(CURATED_DATA_PATH),
                                             dataset_name=info['name'], format='csv')
                    except:
                        df = du.load_dataset(path=str(CURATED_DATA_PATH),
                                             dataset_name=info['name'], format='pkl')
                if df.empty or 'error' in df.columns:
                    st.error(f"No se pudo cargar o el dataset está vacío. Contenido: {df.to_string()}")
                    return
                st.info("Edita filas en la tabla. No olvides guardar.")
                edited_df = st.data_editor(df, num_rows="dynamic",
                                           use_container_width=True, height=600)
                if st.button("💾 Guardar Cambios"):
                    with st.spinner("Guardando cambios..."):
                        du = DataUtilsClass()
                        du.save_dataset(df=edited_df, path=str(CURATED_DATA_PATH),
                                        dataset_name=info['name'], format='csv')
                    st.success("Guardado!")
                    st.rerun()
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
                import traceback
                st.code(traceback.format_exc())

        def render_prompt_editor():
            """Editor de prompts de agente y entorno."""
            st.header("Editor de Prompts para Generación y Chat")
            st.caption("Modifica los prompts. Desmarca 'Activar' para poner `None`.")
            agent_col, env_col = st.columns(2)
            prompt_keys = {
                'agent': ['agent_context', 'agent_source', 'agent_image',
                          'agent_instructions', 'agent_query'],
                'env':   ['env_context', 'env_source', 'env_image',
                          'env_instructions', 'env_query']
            }
            with agent_col:
                st.subheader("🤖 Prompts del Agente")
                st.info("Define comportamiento del agente.")
                for key in prompt_keys['agent']:
                    with st.container():
                        is_active = st.checkbox(
                            f"Activar `{key}`",
                            value=(st.session_state.config.get(key) is not None),
                            key=f"cb_{key}")
                        current = str(st.session_state.config.get(key) or '')
                        st.text_area(f"`{key}`:", value=current,
                                     height=120, key=f"ta_{key}",
                                     disabled=not is_active)
            with env_col:
                st.subheader("🌍 Prompts del Entorno")
                st.info("Define comportamiento del entorno.")
                for key in prompt_keys['env']:
                    with st.container():
                        is_active = st.checkbox(
                            f"Activar `{key}`",
                            value=(st.session_state.config.get(key) is not None),
                            key=f"cb_{key}")
                        current = str(st.session_state.config.get(key) or '')
                        st.text_area(f"`{key}`:", value=current,
                                     height=120, key=f"ta_{key}",
                                     disabled=not is_active)
            st.divider()
            if st.button("💾 Aplicar Cambios en Prompts"):
                with st.spinner("Aplicando..."):
                    for key in prompt_keys['agent'] + prompt_keys['env']:
                        if st.session_state[f"cb_{key}"]:
                            st.session_state.config[key] = st.session_state[f"ta_{key}"]
                        else:
                            st.session_state.config[key] = None
                st.success("Prompts actualizados. Reinicia el chat para que surtan efecto.")

        st.set_page_config(page_title="Personal Assistant", layout="wide", initial_sidebar_state="expanded")
        st.title("🧠 Asistente Personal")

        available_configs = get_available_configs()#configs_module)
        available_configs = [a.replace('.py', '') for a in available_configs]
        try:
            default_config_name = available_configs[0]
        except:
            st.error("No se encontraron diccionarios de configuración en `config.py`.")
            st.stop()

        if 'selected_config_name' not in st.session_state:
            st.session_state.selected_config_name = default_config_name

        module_path = f"{os.environ['PROJECT_NAME']}.configs.{st.session_state.selected_config_name}"
        module = importlib.import_module(module_path)
        config = getattr(module, "config")

        if "main_class" not in st.session_state:
            st.session_state.main_class = MainClass(config)
            st.session_state.history = []
            st.session_state.current_chat_file = None
            st.session_state.config = config.copy()
            st.session_state.view_mode = 'chat'
            st.session_state.viewing_dataset_info = None
            with st.spinner("Inicializando asistente..."):
                try:
                    st.session_state.main_class.initialize(st.session_state.config.copy())
                    st.toast("Asistente inicializado.")
                except Exception as e:
                    st.error(f"Error en inicialización: {e}")
                    st.stop()

        with st.sidebar:
            tab1, tab2, tab3 = st.tabs([
                "⚙️ Configuración y Chats",
                "🛠️ Dataset Generation",
                "🛠️ Tools Setup"
            ])

            # --- PESTAÑA 1: Configuración y Chats ---
            with tab1:
                st.header("Configuración Base")
                selected = st.selectbox("Elige configuración:", available_configs, index=available_configs.index(st.session_state.selected_config_name))
                if selected != st.session_state.selected_config_name:
                    st.session_state.selected_config_name = selected
                    for k in ['main_class','history','current_chat_file',
                              'view_mode','viewing_dataset_info']:
                        st.session_state.pop(k, None)
                    st.success(f"Configuración '{selected}' cargada. Reiniciando...")
                    st.rerun()

                st.divider()
                st.header("Filtros de Chat")
                sel_agent_id = st.multiselect(
                    "Agent ID:", ['USER','AGENT','EVAL'], default=['AGENT'])
                sel_roles    = st.multiselect(
                    "Role:", ['user','assistant','tool','system'],
                    default=['user','assistant', 'tool'])

                st.header("Model & Parámetros")
                model_opts = ["o3", "gpt-5-mini", "o4-mini","gpt-4.1","gpt-4.1-mini","gpt-4.1-nano"]
                default_model = st.session_state.config.get("agent_model","o4-mini")
                agent_model = st.selectbox(
                    "Modelo agente:", model_opts,
                    index=model_opts.index(default_model) if default_model in model_opts else 0
                )
                re_opts = ['low','medium','high',None]
                def_re = st.session_state.config.get("agent_reasoning_effort",None)
                reasoning = st.selectbox("Razonamiento:", re_opts,
                                         index=re_opts.index(def_re))
                delv = st.checkbox("Delete steering",
                                   value=st.session_state.config.get("del_steering",True))
                temp = st.slider("Temperatura:", 0.0, 2.0,
                                 value=float(st.session_state.config.get('temperature',1.0)), step=0.1)
                mode_opts = ["auto","none","required"]
                def_mode = st.session_state.config.get("tool_choice","auto")
                tool_choice = st.selectbox("Tool mode:", mode_opts,
                                           index=mode_opts.index(def_mode) if def_mode in mode_opts else 0)
                if st.button("🚀 Aplicar"):
                    st.session_state.config.update({
                        'agent_model': agent_model,
                        'agent_reasoning_effort': reasoning,
                        'del_steering': delv,
                        'temperature': temp,
                        'tool_choice': tool_choice
                    })
                    with st.spinner("Reconfigurando..."):
                        st.session_state.main_class.initialize(st.session_state.config.copy())
                    st.toast("Configuración aplicada.")

                st.divider()
                st.header("Gestión de Chats")
                if st.button("➕ Nuevo Chat"):
                    st.session_state.history = []
                    st.session_state.current_chat_file = None
                    st.session_state.view_mode = 'chat'
                    st.rerun()

                saved = get_saved_chats()
                if saved:
                    sel = st.selectbox("Cargar chat:", saved, key="sb_saved")
                    c1, c2 = st.columns(2)
                    if c1.button("Cargar"):
                        st.session_state.history = load_chat_history(sel)
                        st.session_state.current_chat_file = sel
                        st.session_state.view_mode = 'chat'
                        st.rerun()
                    if c2.button("Borrar"):
                        if st.session_state.current_chat_file == sel:
                            st.session_state.history = []
                            st.session_state.current_chat_file = None
                        delete_chat_history(sel)
                        st.rerun()

                st.divider()
                st.subheader("Imagen (opcional)")
                image_file = st.file_uploader(
                    "Sube imagen o arrástrala aquí:",
                    type=["png", "jpg", "jpeg", "gif"],
                    help="También puedes pegar la URL abajo."
                )
                image_url = st.text_input("O pega la URL de la imagen:")

            # --- PESTAÑA 2: Dataset Generation ---
            with tab2:
                st.header("Generation Dataset Configuration")
                with st.expander("PASO 1: Generación de dataset"):
                    if "raw_selected" not in st.session_state:
                        st.session_state.raw_selected = []
                    if "url_selected" not in st.session_state:
                        st.session_state.url_selected = []
                    st.subheader("📂 Selección de Fuentes")
                    raw_folders = [f.name for f in RAW_DATA_PATH.iterdir() if f.is_dir()]
                    st.session_state.raw_selected = st.multiselect(
                        "Elige carpetas:", raw_folders,
                        default=st.session_state.raw_selected)
                    st.markdown("---")
                    urls = st.text_area(
                        "Lista de fuentes (URL)",
                        value=st.session_state.config.get('raw_sources', []),
                        height=80
                    ).strip()
                    try:
                        st.session_state.url_selected = eval(urls)
                    except:
                        st.session_state.url_selected = []
                    if not st.session_state.raw_selected and not st.session_state.url_selected:
                        st.warning("Debes elegir una carpeta o introducir al menos una URL.")
                    else:
                        curated_folders = [f.name for f in CURATED_DATA_PATH.iterdir()
                                           if f.is_dir()]
                        if not curated_folders:
                            st.warning("No hay carpetas en CURATED_DATA_PATH.")
                        else:
                            seeds_name = st.text_input(
                                "Nombre dataset de seeds:",
                                value=st.session_state.config.get("seeds_dataset_name","")
                            )
                            seeds_thr = st.number_input(
                                "Seeds chunking threshold:",
                                min_value=10, max_value=100000, step=100,
                                value=st.session_state.config.get("seeds_chunking_threshold",900)
                            )
                            if st.button("Crear dataset"):
                                c = st.session_state.config.copy()
                                c.update({
                                    "seed_chunking_threshold": seeds_thr,
                                    "raw_sources": st.session_state.url_selected +
                                                   st.session_state.raw_selected
                                })
                                with st.spinner("Indexando y creando dataset..."):
                                    st.session_state.main_class.dataset_generation(c)
                                st.success(f"✅ VDB '{seeds_name}' creada.")
                                st.rerun()

                with st.expander("PASO 2: Labeling Automático"):
                    curated_folders = [d.name for d in CURATED_DATA_PATH.iterdir() if d.is_dir()]
                    if not curated_folders:
                        st.warning("Ejecuta antes el PASO 1.")
                    else:
                        use_guidance = st.checkbox("Guidance", value=st.session_state.config.get("use_guidance", True))
                        sel_in      = st.text_input("Dataset entrada:", value=st.session_state.config["gen_input_dataset_name"])
                        gen_out     = st.text_input("Nombre dataset generado:", value=st.session_state.config.get("gen_output_dataset_name",""))
                        hist_out    = st.text_input("Nombre dataset historia:", value=st.session_state.config.get("hist_output_dataset_name",""))
                        n_threads   = st.number_input("Nº hilos (n_thread):", min_value=1, max_value=64, step=1, value=st.session_state.config.get("n_thread",16))
                        max_iter    = st.number_input("Máx iteraciones (gen_max_iter):", min_value=1, max_value=100,value=st.session_state.config.get("gen_max_iter",5))
                        gen_static  = st.checkbox("Usuario estático", value=st.session_state.config.get("gen_static_user",False))
                        use_steer   = st.checkbox("Usar agent steering", value=st.session_state.config.get("gen_use_agent_steering",True))
                        del_steer   = st.checkbox("Eliminar steering tras generación", value=st.session_state.config.get("del_steering",True))
                        user_context = st.text_area("User context", value=st.session_state.config.get('user_context', []), height=100, key='user_context_area').strip()
                        user_instructions = st.text_area("User instructions", value=st.session_state.config.get('user_instructions', []), height=100, key='user_instructions_area').strip()

                        if st.button("Generar dataset"):
                            if not gen_out.strip() or not hist_out.strip():
                                st.error("Define nombres de salida e historia.")
                            else:
                                c = st.session_state.config.copy()
                                c.update({
                                    "gen_input_dataset_name": sel_in,
                                    "gen_output_dataset_name": gen_out.strip(),
                                    "hist_output_dataset_name": hist_out.strip(),
                                    "n_thread": int(n_threads),
                                    "use_guidance": use_guidance,
                                    "gen_max_iter": int(max_iter),
                                    "gen_static_user": bool(gen_static),
                                    "gen_use_agent_steering": bool(use_steer),
                                    "del_steering": bool(del_steer),
                                    "user_context": user_context,
                                    "user_instructions": user_instructions,
                                })
                                with st.spinner("Generando…"):
                                    st.session_state.main_class.dataset_labeling(c)
                                st.success(f"✅ Dataset '{gen_out}' generado.")
                                del st.session_state.main_class
                                st.rerun()

                with st.expander("PASO 3: Fine-Tuning"):
                    gen_datasets = get_dataset_directories(CURATED_DATA_PATH, "")
                    if not gen_datasets:
                        st.warning("Ejecuta antes el PASO 2.")
                    else:
                        sel_hist   = st.text_input("Historia de entrada:", value=st.session_state.config.get('hist_output_dataset_name'))
                        default_ft = st.session_state.config.get('ft_dataset_name', f"{sel_hist}_FT")
                        out_ft     = st.text_input("Directorio salida (FT):", value=default_ft)
                        perc_split = st.slider("Split validación:", 0.01, 0.5,
                                               value=st.session_state.config.get('perc_split',0.2), step=0.01)
                        run_ft     = st.checkbox("Ejecutar Fine-Tuning?",
                                                 value=st.session_state.config.get('run_ft',True))
                        n_epochs   = st.number_input("Epochs:", min_value=1, max_value=100,
                                                     value=st.session_state.config.get('n_epochs',1))
                        avail_models = st.session_state.config.get(
                            'ft_available_models',
                            ['gpt-4.1-nano','gpt-4.1-mini','gpt-4.1','o4-mini'])
                        default_model = st.session_state.config.get('ft_model', avail_models[0])
                        ft_model    = st.selectbox("Modelo FT:", avail_models,
                                                  index=avail_models.index(default_model)
                                                  if default_model in avail_models else 0)
                        if st.button("Iniciar Fine-Tuning"):
                            try:
                                cfg = st.session_state.config.copy()
                                cfg.update({
                                    'gen_output_dataset': sel_hist,
                                    'ft_dataset_name': out_ft,
                                    'perc_split': perc_split,
                                    'run_ft': run_ft,
                                    'n_epochs': n_epochs,
                                    'ft_model': ft_model
                                })
                                st.session_state.main_class.train(cfg)
                                st.success("Job de FT enviado.")
                            except Exception as e:
                                st.error(f"Error en FT: {e}")

                with st.expander("PASO 4: Evaluación"):
                    eval_datasets = get_dataset_directories(CURATED_DATA_PATH, "")
                    if not eval_datasets:
                        st.warning("Ejecuta antes pasos previos.")
                    else:
                        default_in  = st.session_state.config.get('eval_input_dataset_name', eval_datasets[0])
                        sel_eval_in = st.text_input("Dataset entrada:", value=st.session_state.config['eval_input_dataset_name'])
                        eval_out    = st.text_input("Directorio salida:", value=st.session_state.config.get('eval_output_dataset_name',""))
                        hist_eval   = st.text_input("Directorio historia:", value=st.session_state.config.get('eval_hist_output_dataset_name',""))
                        eval_user   = st.checkbox("Usuario estático", value=st.session_state.config.get('eval_static_user',False))
                        eval_iter   = st.number_input("Máx iteraciones:", min_value=1, max_value=1000, value=st.session_state.config.get('eval_max_iter',10))
                        eval_steer  = st.checkbox("Usar Agent Steering", value=st.session_state.config.get('eval_use_agent_steering',False))
                        eval_nthr   = st.slider("Hilos (n_thread):", 1, 32,
                                                value=st.session_state.config.get('n_thread',4))
                        if st.button("Iniciar Evaluación"):
                            try:
                                c = st.session_state.config.copy()
                                c.update({
                                    'eval_input_dataset_name': sel_eval_in,
                                    'eval_output_dataset_name': eval_out,
                                    'eval_hist_output_dataset_name': hist_eval,
                                    'eval_static_user': eval_user,
                                    'eval_max_iter': eval_iter,
                                    'eval_use_agent_steering': eval_steer,
                                    'n_thread': eval_nthr
                                })
                                st.session_state.main_class.eval(c)
                                st.success("Job de Evaluación enviado.")
                            except Exception as e:
                                st.error(f"Error en Evaluación: {e}")
                            del st.session_state.main_class
                            st.rerun()

                with st.expander("PASO 5: Visualización y Edición"):
                    available_datasets = get_dataset_directories(CURATED_DATA_PATH, '')
                    sel_view = st.selectbox("Selecciona dataset:", available_datasets)
                    if st.button("👁️ Ver Dataset"):
                        st.session_state.view_mode = 'dataset_viewer'
                        st.session_state.viewing_dataset_info = {'name': sel_view}
                        st.rerun()

            # --- PESTAÑA 3: Tools Setup (VDB) ---
            with tab3:
                with st.expander("Vector Database Tool"):
                    if "raw_selected" not in st.session_state:
                        st.session_state.raw_selected = []
                    if "url_selected" not in st.session_state:
                        st.session_state.url_selected = []
                    st.subheader("📂 Selección de Fuentes")
                    raw_folders = [f.name for f in RAW_DATA_PATH.iterdir() if f.is_dir()]
                    st.session_state.raw_selected = st.multiselect(
                        "Elige carpetas:", raw_folders,
                        default=st.session_state.raw_selected, key='VDB_raw_sel')
                    st.markdown("---")
                    urls = st.text_area("URLs fuentes", value=st.session_state.config.get('raw_sources',[]), height=100, key='VDB_url_sel').strip()
                    try:
                        st.session_state.url_selected = eval(urls)
                    except:
                        st.session_state.url_selected = []
                    if not st.session_state.raw_selected and not st.session_state.url_selected:
                        st.warning("Selecciona al menos una fuente.")
                    else:
                        curated_folders = [f.name for f in CURATED_DATA_PATH.iterdir() if f.is_dir()]
                        if not curated_folders:
                            st.warning("Ejecuta PASO 1 primero.")
                        else:
                            vdb_name = st.text_input(
                                "Nombre VDB:", value=st.session_state.config.get("vdb_name",""))
                            vdb_thr  = st.number_input(
                                "Chunking threshold:", min_value=100, max_value=10000,
                                step=100, value=st.session_state.config.get("vdb_chunking_threshold",1500))
                            if st.button("Crear VDB"):
                                c = st.session_state.config.copy()
                                c.update({
                                    "indexation_VDB_name": vdb_name,
                                    "vdb_chunking_threshold": vdb_thr,
                                    "raw_sources": st.session_state.raw_selected +
                                                   st.session_state.url_selected
                                })
                                with st.spinner("Indexando VDB..."):
                                    st.session_state.main_class.tools_setup(c)
                                st.success(f"✅ VDB '{vdb_name}' creada.")
                                st.rerun()

        if st.session_state.view_mode == 'dataset_viewer':
            render_dataset_viewer()
        else:
            chat_container = st.container(height=900)
            with chat_container:
                for message in st.session_state.history:
                    if (message.get("agent_id") in sel_agent_id
                            and message.get("channel") in sel_roles):

                        role    = message.get("channel","user")
                        content = message.get("content","")
                        modality     = message.get("modality", None)
                        avatar  = "🧑‍💻" if role=="user" else "🤖"
                        with st.chat_message(role, avatar=avatar):
                            if modality == 'img':
                                st.image(content, width=250)
                            elif modality == 'tool_call':
                                st.json(content, expanded=False)
                            elif role == 'tool':
                                st.json(content, expanded=False)
                            else:
                                display_message(content)

            if prompt := st.chat_input("Escribe tu mensaje aquí..."):
                # Determinar fuente de la imagen (local o URL)
                img_src = None
                if image_file is not None:
                    # Guarda el binario en disco junto al historial
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    fn = f"{ts}_{image_file.name}"
                    save_path = HISTORY_DIR / fn
                    with open(save_path, "wb") as f:
                        f.write(image_file.getbuffer())
                    img_src = str(save_path)
                elif image_url and image_url.strip():
                    img_src = image_url.strip()

                # 4) Enviar al asistente
                # Añadimos primero el mensaje del usuario
                st.session_state.history.append({
                    "agent_id": "USER",
                    "channel": "user",
                    "content": prompt,
                    "img": img_src
                })

                # Preparamos config para la llamada
                call_cfg = st.session_state.config.copy()
                call_cfg['history']      = st.session_state.history
                call_cfg['user_message'] = prompt
                call_cfg['img']          = img_src

                with st.spinner("Pensando..."):
                    try:
                        updated = st.session_state.main_class.predict(call_cfg)
                    except Exception as e:
                        st.error(f"Error procesando tu solicitud: {e}")
                        import traceback; st.code(traceback.format_exc())
                        updated = None

                if updated:
                    st.session_state.history = updated.get('history', [])
                    if st.session_state.current_chat_file is None:
                        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.session_state.current_chat_file = f"chat_{ts}.pkl"
                    save_chat_history(st.session_state.history,
                                      st.session_state.current_chat_file)
                    # Reiniciamos la app para refrescar todo
                    st.rerun()

if __name__ == '__main__':
    FrontEndClass().run()