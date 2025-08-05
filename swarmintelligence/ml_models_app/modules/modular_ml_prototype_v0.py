
"""Modularized prototype"""
def main():
    import os
    from eigenlib.utils.data_utils import DataUtilsClass
    from eigenlib.utils.config_utils import get_config
    os.environ['project_name'] = 'swarmintelligence'
    config = get_config()
    # CONFIG#################################################################################################################
    dataset_name = 'titanic_dataset'
    # df = DataUtilsClass().load_dataset(path=config['data_path'] + '/curated', dataset_name=dataset_name, format='parquet', file_features=False, n_threads=8, cloud=True, overwrite=True)

    from eigenlib.ML.target_feature import TargetFeatureClass
    from eigenlib.ML.identity import IdentityClass
    from eigenlib.ML.imputer import ImputerClass
    from eigenlib.ML.basic_validation_split import BasicValidationSplitClass
    from eigenlib.ML.feature_scaling import FeatureScalingClass
    from eigenlib.ML.feature_category_encoder import FeatureCategoryEncoderClass
    from eigenlib.ML.lgbm_model import LGBMModelClass
    from eigenlib.ML.metrics_classification_regression import MetricsClassificationRegressionClass
    from eigenlib.ML.wandb_logging import WandbLoggingClass
    from eigenlib.ML.basic_model_loader import BasicModelLoaderClass
    from eigenlib.ML.general_ml_pipeline import GeneralMLPipelineClass

    data = {
        'hypothesis': '',
        'model_id': 'titanic_test_v0',
        'to_cloud': False,
        'checkpoint': 1,
        'dataset_name': 'titanic_dataset',
        'hparams_grid': {'num_boost_round': 0.001},
        'main_metric': 'accuracy',
        'LGBM_params_dict': {
            'boosting_type': 'gbdt',
            'objective': 'binary',
            'metric': 'accuracy',
            'n_estimators': 1000,
            'learning_rate': 0.01,
            'num_leaves': 32,
            'max_depth': 6,
            'min_child_samples': 20,
            'subsample': 0.8,
            'subsample_freq': 1,
            'colsample_bytree': 0.8,
            'reg_alpha': 0.1,
            'reg_lambda': 0.1,
            'random_state': 42,
            'n_jobs': -1,
            'verbosity': -1
        },
        'tuning_direction': 'maximize',
        'tuning_trials': 3,
    }

    spp_1 = TargetFeatureClass(target_features=['target'])
    spp_2 = ImputerClass(cat_strategy='', num_strategy='')
    spp_3 = IdentityClass()
    val_split = BasicValidationSplitClass(42, 0.7, 0.15, 0.15, split_feature=None)
    dpp_1 = FeatureScalingClass('StandardScaler', scaling_features=[])
    dpp_2 = FeatureCategoryEncoderClass('TargetEncoder', encoding_features=['sex', 'class', 'deck', 'embark_town', 'alone'])
    dpp_3 = IdentityClass()
    dpp_4 = IdentityClass()
    model = LGBMModelClass(params_dict=data.get('LGBM_params_dict', {}), problem_mode='classification', categories=[0, 1], use_calibration=False, prediction_mode='predict')
    pos_1 = IdentityClass()
    pos_2 = IdentityClass()
    pos_3 = IdentityClass()
    metrics = MetricsClassificationRegressionClass(mode='classification', average=None)
    logger = WandbLoggingClass(run_name=None, project_name=None, logging=False)
    model_loader = BasicModelLoaderClass(cloud=True, save_model=False)

    PL = GeneralMLPipelineClass(data, ETL=None, spp_1=spp_1, spp_2=spp_2, spp_3=spp_3, val_split=val_split, dpp_1=dpp_1, dpp_2=dpp_2, dpp_3=dpp_3, dpp_4=dpp_4, model=model, pos_1=pos_1, pos_2=pos_2, metrics=metrics, logger=logger, model_loader=model_loader)
    score_df = PL.train()

    import optuna
    def objective(trial):
        ################################################################################################################
        data['LGBM_params_dict']['num_boost_round'] = trial.suggest_int('num_boost_round', 500, 1500)
        data['LGBM_params_dict']['feature_fraction'] = trial.suggest_float('feature_fraction', 0.4, 1.0)
        data['LGBM_params_dict']['learning_rate'] = trial.suggest_float('learning_rate', 0.0005, 0.05)
        data['LGBM_params_dict']['colsample_bytree'] = trial.suggest_float('colsample_bytree', 0.4, 1.0)
        data['LGBM_params_dict']['max_depth'] = trial.suggest_int('max_depth', 3, 15)
        data['LGBM_params_dict']['min_child_samples'] = trial.suggest_int('min_child_samples', 10, 100)
        data['LGBM_params_dict']['reg_alpha'] = trial.suggest_float('reg_alpha', 1e-4, 10.0)
        data['LGBM_params_dict']['reg_lambda'] = trial.suggest_float('reg_lambda', 1e-4, 10.0)
        data['LGBM_params_dict']['boosting_type'] = trial.suggest_categorical('boosting_type', ['gbdt'])
        data['switch_1'] = trial.suggest_categorical('switch_1', [True, False])
        ################################################################################################################
        PL = GeneralMLPipelineClass(data, ETL=None, spp_1=spp_1, spp_2=spp_2, spp_3=spp_3, val_split=val_split, dpp_1=dpp_1, dpp_2=dpp_2, dpp_3=dpp_3, dpp_4=dpp_4, model=model, pos_1=pos_1, pos_2=pos_2, metrics=metrics, logger=logger, model_loader=model_loader)
        score_df = PL.train()
        score = score_df[data['main_metric']][0]
        return score

    study = optuna.create_study(direction=data['tuning_direction'])
    study.optimize(objective, n_trials=data['tuning_trials'])
    best_params = study.best_trial.params
    data['LGBM_params_dict']['num_boost_round'] = best_params['num_boost_round']
    data['LGBM_params_dict']['feature_fraction'] = best_params['feature_fraction']
    data['LGBM_params_dict']['learning_rate'] = best_params['learning_rate']
    data['LGBM_params_dict']['colsample_bytree'] = best_params['colsample_bytree']
    data['LGBM_params_dict']['max_depth'] = best_params['max_depth']
    data['LGBM_params_dict']['min_child_samples'] = best_params['min_child_samples']
    data['LGBM_params_dict']['reg_alpha'] = best_params['reg_alpha']
    data['LGBM_params_dict']['reg_lambda'] = best_params['reg_lambda']
    data['LGBM_params_dict']['boosting_type'] = best_params['boosting_type']

if __name__ == "__main__":
    main()