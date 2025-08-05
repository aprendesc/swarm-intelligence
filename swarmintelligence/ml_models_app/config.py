
"""Config v0"""
hypothesis = """Pruebas basicas con titanic"""
from swarmintelligence.ml_models_app.modules.titanic_model import TitanicModelClass
version = 'v0'
test_config = {
            'hypothesis': hypothesis,
            'version': version,
            #INITIALIZE
            'model_class': TitanicModelClass,
            #ETL
            'n_shards': 1,
            'cloud': False,
            'dataset_name': 'titanic_dataset',
            #TRAIN
            'model_id': 'titanic_test_v0',
            'to_cloud': False,
            'checkpoint': 1,
            'hparams_grid': {'num_boost_round': 0.001},
            'main_metric': 'accuracy',
            'Catboost_params_dict': {
                        'iterations': 1000,
                        'learning_rate': 0.01,
                        'depth': 6,
                        'loss_function': 'Logloss',
                        'eval_metric': 'Accuracy',
                        'cat_features': [],
                        'random_state': 42,
                        'logging_level': 'Silent',
                        'early_stopping_rounds': 20,
                        'subsample': 0.8,
                        'colsample_bylevel': 0.8,
                        'l2_leaf_reg': 3,
                        'border_count': 32,
                        'thread_count': -1,
                    },
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
            'XGB_params_dict': {
                "objective": "binary:logistic",
                "eval_metric": "logloss",
                "booster": "gbtree",
                "max_depth": 4,
                "min_child_weight": 1,
                "gamma": 0.1,
                "learning_rate": 0.05,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "reg_alpha": 0.01,
                "reg_lambda": 1.0,
                "num_boost_round": 500,
                "early_stopping_rounds": 20
            },
            'tuning_direction': 'maximize',
            'tuning_trials': 2,
            #EVAL
            #SERVING
            'endpoint_name': '',
            'script': '/Repos/alejandropca@ext.inditex.com/swarm-intelligence-project/swarmintelligence/launcher.py'
        }

########################################################################################################################

simple_llm_config = {}



