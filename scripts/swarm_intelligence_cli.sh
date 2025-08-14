# Añadir PROJECT_NAME
export PROJECT_NAME="swarmintelligence"
export PROJECT_FOLDER="swarm-intelligence"

# Cambiar al directorio del proyecto
cd "C:/Users/$USERNAME/Desktop/proyectos/$PROJECT_FOLDER" || exit

# Configurar PYTHONPATH
export PYTHONPATH="/c/Users/$USERNAME/Desktop/proyectos/$PROJECT_FOLDER:/c/Users/$USERNAME/Desktop/proyectos/eigenlib"

# Activar el entorno virtual
source ".venv/Scripts/activate"

# Cargar variables de entorno desde el archivo .env (ignorando comentarios)
export $(grep -v '^#' .env | xargs)

# Asegurar salida no bufferizada en Python
export PYTHONUNBUFFERED=1

# Ejecutar la CLI de swarmml
python -c """from eigenlib.utils.auto_cli import AutoCLI; AutoCLI().run()"""