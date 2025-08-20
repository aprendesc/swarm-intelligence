# Añadir PROJECT_NAME
export BASE_PATH="C:/Users/$USERNAME/Desktop/proyectos/"
export REPO_FOLDER="swarm-intelligence"
export MODULE_NAME="swarmintelligence"

# Cambiar al directorio del proyecto
cd "$BASE_PATH/$REPO_FOLDER" || exit

# Configurar PYTHONPATH
export PYTHONPATH="$BASE_PATH/eigenlib"

# Activar el entorno virtual
source ".venv/Scripts/activate"

# Cargar variables de entorno desde el archivo .env (ignorando comentarios)
export $(grep -v '^#' .env | xargs)

# Asegurar salida no bufferizada en Python
export PYTHONUNBUFFERED=1

# Ejecutar la CLI de swarmml
python -c """from eigenlib.utils.auto_cli import AutoCLI; AutoCLI().run()"""