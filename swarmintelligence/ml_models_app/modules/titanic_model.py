
class TitanicModelClass:
    def __init__(self, config):
        self.hiposthesis = 'Modelo titanic de pruebas'

    def ETL(self, config={}):
        from eigenlib.ML.etl_dummy import ETLDummyClass
        dataset_name = config.get('data_name', 'titanic_dataset')
        n_shards = config.get('n_shards', 1)
        cloud = config.get('cloud', False)
        X, y, config = ETLDummyClass(dataset_name=dataset_name, n_shards=n_shards, cloud=cloud).run()
        return config

    def train(self, config):
        from eigenlib.ML.target_feature import TargetFeatureClass
        from eigenlib.ML.identity import IdentityClass
        from eigenlib.ML.imputer import ImputerClass
        from eigenlib.ML.basic_validation_split import BasicValidationSplitClass
        from eigenlib.ML.feature_scaling import FeatureScalingClass
        from eigenlib.ML.feature_category_encoder import FeatureCategoryEncoderClass
        from eigenlib.ML.lgbm_model import LGBMModelClass
        from eigenlib.ML.xgb_model import ModelXGBClass
        from eigenlib.ML.catboost_model import ModelCatboostClass
        from eigenlib.ML.pytorn_nn_model_v2 import PytorchNNModelClass
        from eigenlib.ML.ensemble_model import BlendingEnsemble
        from eigenlib.ML.metrics_classification_regression import MetricsClassificationRegressionClass
        from eigenlib.ML.wandb_logging import WandbLoggingClass
        from eigenlib.ML.basic_model_loader import BasicModelLoaderClass
        from eigenlib.ML.general_ml_pipeline import GeneralMLPipelineClass
        ################################################################################################################
        spp_1 = TargetFeatureClass(target_features=['target'])
        spp_2 = ImputerClass(cat_strategy='', num_strategy='')
        spp_3 = IdentityClass()
        val_split = BasicValidationSplitClass(42, 0.8, 0.02, 0.18, split_feature=None)
        dpp_1 = FeatureScalingClass('StandardScaler', scaling_features=[])
        dpp_2 = FeatureCategoryEncoderClass('TargetEncoder', encoding_features=['sex', 'class', 'deck', 'embark_town', 'alone'])
        dpp_3 = IdentityClass()
        dpp_4 = IdentityClass()
        model_base_0 = PytorchNNModelClass(learning_rate=0.001, batch_size=64, epochs=100, early_stopping_patience=10, hidden_size=7, dropout_rate=0.2, device='cuda', print_every=10)
        model_base_1 = ModelCatboostClass(params_dict=config.get('Catboost_params_dict', {}), problem_mode='classification', categories=[0, 1], use_calibration=False, prediction_mode='predict')
        model_base_2 = ModelXGBClass(params_dict=config.get('XGB_params_dict', {}), problem_mode='classification', categories=[0, 1], use_calibration=False, prediction_mode='predict')
        metamodel = LGBMModelClass(params_dict=config.get('LGBM_params_dict', {}), problem_mode='classification', categories=[0, 1], use_calibration=False, prediction_mode='predict')
        model = BlendingEnsemble([model_base_0, model_base_1, model_base_2], metamodel, problem_mode='classification', test_size_meta=0.3, random_state=42)
        pos_1 = IdentityClass()
        pos_2 = IdentityClass()
        metrics = MetricsClassificationRegressionClass(mode='classification', average=None)
        logger = WandbLoggingClass(run_name=None, project_name=None, logging=False)
        model_loader = BasicModelLoaderClass(cloud=config.get('cloud', False), save_model=True)
        ################################################################################################################
        PL = GeneralMLPipelineClass(config, ETL=None, spp_1=spp_1, spp_2=spp_2, spp_3=spp_3, val_split=val_split, dpp_1=dpp_1, dpp_2=dpp_2, dpp_3=dpp_3, dpp_4=dpp_4, model=model, pos_1=pos_1, pos_2=pos_2, metrics=metrics, logger=logger, model_loader=model_loader)
        score_df = PL.train()
        config['score_df'] = score_df
        return config

    def hparam_tuning(self, config):
        import optuna
        import copy
        self.config = copy.deepcopy(config)
        def objective(trial):
            ################################################################################################################
            self.config['LGBM_params_dict']['num_boost_round'] = trial.suggest_int('num_boost_round', 500, 1500)
            self.config['LGBM_params_dict']['feature_fraction'] = trial.suggest_float('feature_fraction', 0.4, 1.0)
            self.config['LGBM_params_dict']['learning_rate'] = trial.suggest_float('learning_rate', 0.0005, 0.05)
            self.config['LGBM_params_dict']['colsample_bytree'] = trial.suggest_float('colsample_bytree', 0.4, 1.0)
            self.config['LGBM_params_dict']['max_depth'] = trial.suggest_int('max_depth', 3, 15)
            self.config['LGBM_params_dict']['min_child_samples'] = trial.suggest_int('min_child_samples', 10, 100)
            self.config['LGBM_params_dict']['reg_alpha'] = trial.suggest_float('reg_alpha', 1e-4, 10.0)
            self.config['LGBM_params_dict']['reg_lambda'] = trial.suggest_float('reg_lambda', 1e-4, 10.0)
            self.config['LGBM_params_dict']['boosting_type'] = trial.suggest_categorical('boosting_type', ['gbdt'])
            self.config['switch_1'] = trial.suggest_categorical('switch_1', [True, False])
            ################################################################################################################
            config = self.train(self.config)
            score_df = config['score_df']
            score = score_df[config['main_metric']][0]
            return score

        study = optuna.create_study(direction=config['tuning_direction'])
        study.optimize(objective, n_trials=config['tuning_trials'])
        best_params = study.best_trial.params
        config['best_params'] = best_params
        config['LGBM_params_dict']['num_boost_round'] = best_params['num_boost_round']
        config['LGBM_params_dict']['feature_fraction'] = best_params['feature_fraction']
        config['LGBM_params_dict']['learning_rate'] = best_params['learning_rate']
        config['LGBM_params_dict']['colsample_bytree'] = best_params['colsample_bytree']
        config['LGBM_params_dict']['max_depth'] = best_params['max_depth']
        config['LGBM_params_dict']['min_child_samples'] = best_params['min_child_samples']
        config['LGBM_params_dict']['reg_alpha'] = best_params['reg_alpha']
        config['LGBM_params_dict']['reg_lambda'] = best_params['reg_lambda']
        config['LGBM_params_dict']['boosting_type'] = best_params['boosting_type']
        score_df = self.train(config)
        config['score_df'] = score_df
        print('FINAL TRAINING=================================================================')
        return config

    def eval(self, config):
        from eigenlib.ML.basic_model_loader import BasicModelLoaderClass
        model_loader = BasicModelLoaderClass(cloud=config.get('cloud', False), save_model=False)
        PL = model_loader.load(config['model_id'])
        analytics_data = PL.analytics_data
        X_test = analytics_data['X_test']
        y_test = analytics_data['y_test']
        y_pred_test = PL.inference(X_test, {})
        score_df, metadata = PL.metrics.run(y_test, y_pred_test, PL.metadata)
        print(score_df)

    def run_front(self):
        pass

    def predict(self, config={}):
        return config

    def serving(self):
        # sv = Serving(**d).deploy_endpoint()
        # data = Serving(**d).call_endpoint(d)
        pass
