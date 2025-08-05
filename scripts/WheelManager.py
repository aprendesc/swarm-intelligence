import subprocess
import os
import json
from azure.storage.blob import BlobServiceClient

def cloud_delete(cloud_path, filename, STORAGEACCOUNTURL, STORAGEACCOUNTKEY, CONTAINERNAME):
    BLOBNAME = cloud_path + '/' + filename
    blob_service_client = BlobServiceClient(account_url=STORAGEACCOUNTURL, credential=STORAGEACCOUNTKEY)
    blob_client = blob_service_client.get_blob_client(container=CONTAINERNAME, blob=BLOBNAME)
    try:
        blob_client.delete_blob()
    except:
        pass

def cloud_explore(cloud_path, STORAGEACCOUNTURL, STORAGEACCOUNTKEY, CONTAINERNAME):
    BLOBNAME = cloud_path
    blob_service_client_instance = BlobServiceClient(account_url=STORAGEACCOUNTURL, credential=STORAGEACCOUNTKEY)
    a = blob_service_client_instance.get_container_client(CONTAINERNAME)
    names = []
    for blob in a.list_blobs(name_starts_with=BLOBNAME):
        names.append(blob['name'])
    return names

def cloud_upload_file(local_path, cloud_path, filename, STORAGEACCOUNTURL, STORAGEACCOUNTKEY, CONTAINERNAME):
    local_path = local_path + '/' + filename
    final_path = cloud_path + '/' + filename
    blob_service_client_instance = BlobServiceClient(account_url=STORAGEACCOUNTURL, credential=STORAGEACCOUNTKEY)
    blob_client_instance = blob_service_client_instance.get_blob_client(CONTAINERNAME, final_path, snapshot=None)
    file = final_path.replace('./', '')
    if file in cloud_explore(cloud_path, STORAGEACCOUNTURL, STORAGEACCOUNTKEY, CONTAINERNAME):
        cloud_delete(cloud_path, filename, STORAGEACCOUNTURL, STORAGEACCOUNTKEY, CONTAINERNAME)
    with open(local_path, "rb") as data:
        blob_client_instance.upload_blob(data)

def cloud_download_file(local_path, cloud_path, filename, STORAGEACCOUNTURL, STORAGEACCOUNTKEY, CONTAINERNAME):
    BLOBNAME = cloud_path + '/' + filename
    final_path = local_path + '/' + filename
    blob_service_client_instance = BlobServiceClient(account_url=STORAGEACCOUNTURL, credential=STORAGEACCOUNTKEY)
    blob_client_instance = blob_service_client_instance.get_blob_client(CONTAINERNAME, BLOBNAME, snapshot=None)
    blob_client_instance.download_blob()
    with open(final_path, "wb") as download_file:
        download_file.write(blob_client_instance.download_blob().readall())
    print(f'{filename} downloaded into {local_path}')

def get_config(config_path='./config/config.json'):
    """Load the config file and gets the environent variables"""
    try:
        with open(config_path, 'r') as json_file:
            config = json.load(json_file)
    except:
        config_path = '.' + config_path
        with open(config_path, 'r') as json_file:
            config = json.load(json_file)

    project_config = config['project_name']
    platform = os.environ['platform']
    os.environ['data_path'] = config[platform + '_data_path']
    os.environ['models_path'] = config[platform + '_models_path']
    os.environ['project_path'] = config[platform + '_project_path']
    config['cloud_data_path'] = config['cloud_data_path']
    config['cloud_models_path'] = config['cloud_models_path']
    config['data_path'] = config[platform + '_data_path']
    config['models_path'] = config[platform + '_models_path']
    config['project_path'] = config[platform + '_project_path']
    config['platform'] = platform
    return config

class WheelManager:
    def __init__(self):
        #os.environ['platform'] = 'local'
        config = get_config()
        self.wheel_name = 'eigenlib-0.1-py3-none-any.whl'
        self.local_path = config['data_path'] + '/raw'
        self.cloud_path = config['cloud_data_path'] + '/wheels'
        self.package_path = 'C:/Users/AlejandroPrendesCabo/Desktop/proyectos/eigenlib/'
        self.STORAGEACCOUNTURL = config['STORAGEACCOUNTURL']#'https://pocfashionstorage.blob.core.windows.net/'
        self.STORAGEACCOUNTKEY = config['STORAGEACCOUNTKEY']#'sp=racwdli&st=2024-07-26T12:30:41Z&se=2025-10-22T20:30:41Z&spr=https&sv=2022-11-02&sr=c&sig=AQ9pXMC3e%2FN%2F2JNHn6%2FmcC2hxnQIbr0cgqVJYyGmi88%3D'
        self.CONTAINERNAME = config['CONTAINERNAME']#'suqi-lab'

    def build(self):
        #subprocess.check_call([os.sys.executable, self.path + 'setup.py', 'bdist_wheel'])
        command = f'cd {self.package_path} && {os.sys.executable} setup.py bdist_wheel && exit'
        subprocess.Popen(['start', 'cmd', '/k', command], shell=True)
        local_wheel_path = self.package_path + 'dist/'
        cloud_upload_file(local_wheel_path, self.cloud_path, 'eigenlib-0.1-py3-none-any.whl', self.STORAGEACCOUNTURL, self.STORAGEACCOUNTKEY, self.CONTAINERNAME)

    def install(self):
        cloud_download_file(self.local_path, self.cloud_path, 'eigenlib-0.1-py3-none-any.whl', self.STORAGEACCOUNTURL,self.STORAGEACCOUNTKEY, self.CONTAINERNAME)
        subprocess.check_call([os.sys.executable, '-m', 'pip', 'install', self.local_path + '/' + self.wheel_name, '--force-reinstall'])

    def uninstall(self):
        command = os.sys.executable + ' -m pip uninstall ' + self.local_path + '/' + self.wheel_name + ' && exit'
        subprocess.Popen(['start', 'cmd', '/k', command], shell=True)

#WheelManager().build()
#WheelManager().install()
#WheelManager().uninstall()