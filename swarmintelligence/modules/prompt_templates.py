import os
from pathlib import Path
from eigenlib.utils.project_setup import ProjectSetupClass

ProjectSetupClass(project_name='swarmintelligence', app_name='personal_assistant')

def generate_code_assistant_prompt(path):
    #app_name = path.split('/')[-1]
    #project_name = path.split('/')[-2]
    #project_folder = path.split('/')[-3]
    root = '/'.join(path.split('/')[0:-3])
    with open(path + '/test.py', 'r', encoding='utf-8') as archivo:
        test_code = archivo.read()
    with open(path + '/main.py', 'r', encoding='utf-8') as archivo:
        main_code = archivo.read()
    with open(path + '/config.py', 'r', encoding='utf-8') as archivo:
        config_code = archivo.read()

    eigenlib_path = root + '/eigenlib/eigenlib'
    with open(eigenlib_path + '/test.py', 'r', encoding='utf-8') as archivo:
        eigenlib_tests = archivo.read()

    def leer_todos_los_py(directorio):
        ruta_dir = Path(directorio)
        codigo_total = ""

        if not ruta_dir.exists():
            print(f"El directorio no existe: {directorio}")
            return ""

        archivos_py = ruta_dir.rglob('*.py')  # Usa glob() si no quieres incluir subdirectorios

        for archivo in archivos_py:
            try:
                with archivo.open('r', encoding='utf-8') as f:
                    codigo_total += f"\n# --- Archivo: {archivo} ---\n"
                    codigo_total += f.read() + "\n"
            except Exception as e:
                print(f"No se pudo leer {archivo}: {e}")

        return codigo_total

    path = os.path.join(path, 'modules')
    modulos = leer_todos_los_py(path)

    prompt = f"""
# Todos mis proyectos estan compuestos por los siguientes scripts:
    modules/-> En este directorio estan los modulos generales que usa la clase personal_assistant_main_v0.py
    config.py -> En config se muestran todas las configuraciones del proyecto, diccionarios empleados con todos los parámetros para ser empleados por la clase main
    main.py -> Contiene la clase principal de la aplicación con todos sus métodos de ejecución principales.
    test.py -> Contiene todos los tests de las funciones principales de la aplicación. Se usa como launcher y comprobación.

# CODIGO DE TEST:
En test se encuentran los métodos de ejecución del proyecto formulados como test:

python'''{test_code}'''

Son todas las formas de ejecutar el proyecto.

# CODIGO DE MAIN:
En main se encuentra la clase principal:

python'''{main_code}''' 

# CODIGO DE CONFIG
En config se encuentran los diccionarios de configuracion que recibe la clase main y que tambien formará parte de las
llamadas via api que enviaremos desde el frontal, por lo que este diccionario sirve como interfaz de configuración de 
los experimentos:

python'''{config_code}''' 

# MODULOS DEL PROYECTO:

Además contamos con los siguientes modulos que se emplean en main:

{modulos}

# EJEMPLOS DE PRUEBAS DEL FRAMEWORK PERSONAL:

Se muetran los siguientes ejemplos clave de cómo usar las diferentes utilidades del framework:

python'''{eigenlib_tests}'''

# ESTRUCTURAS DE DATOS:
Se trata de un proyecto modularizado con un arquetipo estandar.
Todas las fuentes de datos se guardan en ./data que contiene
./data/raw -> almacenamiento de orígenes: subcarpetas de descargas y extracciones planas de ficheros Excel/PDF.
./data/curated -> datos intermedios tras cada paso ETL: CSVs con imágenes extraídas, curación visual, normalización de formatos, mapas de términos.
./data/processed -> Para fuentes finales, entregables, informes...
./data/models/ -> almacenamiento y carga de modelos entrenados o fine-tuned.

Los archivos disponibles en raw son:

os.path.join(root, project_folder, 'data/raw/', app_name)
{str(os.listdir('/'.join(path.split('/')[0:-2]) + '/data/raw/'))}

Los datasets disponibles en curated son:
{str(os.listdir('/'.join(path.split('/')[0:-2]) + '/data/curated/'))}

# INSTRUCCIONES:
* Para cargar el environment y poder ejecutar código usa siempre:
* Sigue las instrucciones del usuario empleando el mismo estilo de los códigos de la codebase.

"""
    return prompt