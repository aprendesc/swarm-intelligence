from eigenlib.utils.encryption_utils import EncryptionUtilsClass
import os
from eigenlib.utils.project_setup import ProjectSetupClass
ProjectSetupClass(project_name='swarmintelligence', app_name='automations')
################################################################################################################
EU = EncryptionUtilsClass()
file = os.path.join(os.environ['PROJECT_NAME'], 'env', '.env')
password = input('Password: ')
EU.encrypt_file(file, file + '.enc', password=password)
