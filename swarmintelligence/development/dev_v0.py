import sys, os
from eigenlib.utils.project_setup import ProjectSetup
########################################################################################################################
os.environ['BASE_PATH'] = f'C:/Users/{os.environ["USERNAME"]}/Desktop/proyectos'
os.environ['REPO_FOLDER'] = 'swarm-intelligence'
os.environ['MODULE_NAME'] = 'swarmintelligence'
path_dirs = [
                os.path.join(os.environ['BASE_PATH'], 'swarm-ml'),
                os.path.join(os.environ['BASE_PATH'], 'swarm-intelligence'),
                os.path.join(os.environ['BASE_PATH'], 'swarm-automations'),
                os.path.join(os.environ['BASE_PATH'], 'swarm-compute'),
                os.path.join(os.environ['BASE_PATH'], 'eigenlib'),
                ]
sys.path.extend([os.path.join(os.environ['BASE_PATH'], 'eigenlib')])
########################################################################################################################
ps = ProjectSetup()
ps.init()
ps.coverage()
########################################################################################################################
# PROJECT SERVER
import os
from swarmautomations.main import MainClass as SAMainClass
config = {
    'launch_master': False,
    'node_name': os.environ['MODULE_NAME'],
    'node_delay': 1
}
sa_main = SAMainClass(config).deploy_project_server(config)
########################################################################################################################

#TEMPLATES
class MyClass:
    def __init__(self):
        pass

    def run(self):
        print('Hola Mundo!')

class TestMyClass(unittest.TestCase):
    def SetUp(self):
        pass

    def test_run(self):
        mc = MyClass()
        mc.run()

"""
Vamos a modificar el main.py para incluir un modo replace, de manera que se incluya un nuevo argumento que sea content_to_replace y el nuevo modo.

Debe estar programado exactamente igual que yo suelo programar todo, mismo estilo. El resto de la clase debe quedar EXACTAMENTE igual.
"""


