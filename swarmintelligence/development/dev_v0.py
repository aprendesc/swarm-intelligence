import sys, os
from eigenlib.utils.project_setup import ProjectSetup
########################################################################################################################
os.environ['BASE_PATH'] = f'C:/Users/{os.environ["USERNAME"]}/Desktop/proyectos'
os.environ['REPO_FOLDER'] = 'swarm-intelligence'
os.environ['MODULE_NAME'] = 'swarmintelligence'
########################################################################################################################
ps = ProjectSetup()
ps.init()
ps.coverage()
########################################################################################################################

if False:
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

