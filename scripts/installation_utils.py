import ast
import os
import sys
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError
from eigenlib.utils.project_setup import ProjectSetupClass
project_name = inpur('Project name: ')
ProjectSetupClass(project_name=project_name, app_name='')
#CREATE THE REQUIREMENTS.TXT
def find_imports(d):
    di, fi = set(), set()
    for f in Path(d).rglob('*.py'):
        try:
            tree = ast.parse(f.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"Error leyendo {f}: {e}", file=sys.stderr)
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                di |= {x.name.split('.')[0] for x in n.names}
            if isinstance(n, ast.ImportFrom) and n.module:
                fi.add(n.module.split('.')[0])
    return di | fi  # Unión de ambos sets
def get_installed_versions(modules):
    requirements = []
    for mod in sorted(modules):
        try:
            ver = version(mod)
            requirements.append(f"{mod}=={ver}")
        except PackageNotFoundError:
            print(f"# {mod} no encontrado en el entorno", file=sys.stderr)
    return '\n'.join(requirements)
d = './' + os.environ['PROJECT_NAME']
mods = find_imports(d)
reqs_str = get_installed_versions(mods)
print(reqs_str)

#CREATE THE .ENV
"""
PROJECT_FOLDER=outfit-generator-2-poc
PROJECT_NAME=og2poc

RAW_DATA_PATH=data/raw
CURATED_DATA_PATH=data/curated
PROCESSED_DATA_PATH=data/processed

LOCAL_PROJECT_ROOT=C:/Users/AlejandroPrendesCabo/Desktop/proyectos
LOCAL_2_PROJECT_ROOT=C:/Users/apren/Desktop/proyectos
DB_PROJECT_ROOT=/dbfs/FileStore/APC_storage
ENDPOINT_PROJECT_ROOT=/opt/conda/envs/mlflow-env/lib/python3.11/site-packages
CLOUD_PROJECT_ROOT=/dbfs/FileStore/APC_cloud_storage

DB_REPO_ID=564247559775205

OAI_SUBS_1=https://ccconvai-openai-swc1-dev-001.openai.azure.com/
OAI_API_KEY_1=b5d39eaea47e46328d12a7785d63cd5e
OAI_API_VERSION_1=2025-03-01-preview

OAI_SUBS_2=https://openai-openai-swc1-pro-001.openai.azure.com/
OAI_API_KEY_2=88e7710a6d4a437793b1ea9aa5069672
OAI_API_VERSION_2=2025-03-01-preview

DATABRICKS_INSTANCE=
DB_TOKEN=

TELEGRAM_BOT_TOKEN_1=
TELEGRAM_CHAT_ID1=

NGROK_TOKEN=

CONNECTION_STRING =

SNOWFLAKE_ACCOUNT =
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_DATABASE=
SNOWFLAKE_SCHEMA=
SNOWFLAKE_WAREHOUSE=

AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
KAIA_URL=

WANDB_API_KEY=

"""


