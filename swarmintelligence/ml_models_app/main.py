from eigenlib.utils.project_setup import ProjectSetupClass
ProjectSetupClass(project_name='swarmintelligence', app_name='ml_models')

class MainClass:
    def __init__(self, config):
        self.model = config['model_class']

    def ETL(self, config):
        config = self.model(config).ETL(config)
        return config

    def train(self, config):
        config = self.model(config).train(config)
        return config

    def hparam_tuning(self, config):
        config = self.model(config).hparam_tuning(config)
        return config

    def eval(self, config):
        config = self.model(config).eval(config)
        return config

    def predict(self, config):
        config = self.model(config).predict(config)
        return config

if __name__ == "__main__":
    from swarmintelligence.ml_models_app.config import test_config as config
    main = MainClass(config)
    #main.ETL(config)
    #main.train(config)
    main.eval(config)
    #main.hparam_tuning(config)
    #main.predict(config)
    #main.run_frontend(
