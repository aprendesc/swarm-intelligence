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

from eigenlib.utils.data_utils import DataUtilsClass
source_df = DataUtilsClass().load_dataset(path=os.environ['CURATED_DATA_PATH'], dataset_name='test_assistant_GEN_HIST', format='csv')
source_df = source_df[source_df['agent_id']=='AGENT']
source_df = source_df[source_df['steering'] == False]


import pandas as pd


out = str(conversor(source_df)[0:10])



aux = pd.Series(out).apply(lambda x: x['messages'][3])


import dask.dataframe as dd
import pandas as pd

# Ejemplo: DataFrame grande
df = pd.DataFrame({
    "id": range(100_000),
    "valor": range(100_000)
})

# Convertimos a Dask DataFrame con particiones
ddf = dd.from_pandas(df, npartitions=10)

# Guardar en particiones CSV
ddf.to_csv("data/curated/partitions/dataset_*.csv", index=False)













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

