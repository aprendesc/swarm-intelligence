cd C:/Users/$USERNAME/Desktop/proyectos/swarm-intelligence
export PYTHONPATH=/c/Users/$USERNAME/Desktop/proyectos/swarm-intelligence:/c/Users/$USERNAME/Desktop/proyectos/eigenlib
source .venv/Scripts/activate
export PYTHONUNBUFFERED=1
python -c "
from eigenlib.utils.project_setup import ProjectSetupClass
ProjectSetupClass(project_folder='swarm-intelligence')
import os
import pandas as pd
from swarmintelligence.main import MainClass
from swarmintelligence.config import gp_assistant_config as config
main=MainClass(config)
main.launch_front(config)
"