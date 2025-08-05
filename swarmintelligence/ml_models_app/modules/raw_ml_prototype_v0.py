
"""Raw prototype"""
def main():
    import os
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    from sklearn.impute import SimpleImputer
    from category_encoders import TargetEncoder
    import lightgbm as lgb
    import optuna
    from eigenlib.utils.data_utils import DataUtilsClass
    from eigenlib.utils.config_utils import get_config
    os.environ['project_name'] = 'swarmintelligence'
    config = get_config()

    #ETL
    X = pd.read_csv('https://storage.googleapis.com/tf-datasets/titanic/train.csv')
    y = X[['survived']]
    X = X.drop(columns=['survived'])
    X['target'] = y
    DataUtilsClass.save_dataset(X, path=config['data_path'] + '/curated', dataset_name='titanic_dataset', format='parquet', shard_key=None, shard_name=None, file_features=False, n_shards=1, n_threads=8, cloud=False, )

    #DATA LOAD
    df = DataUtilsClass().load_dataset(path=config['data_path'] + '/curated', dataset_name='titanic_dataset', format='parquet', selected_shards=[], file_features=True, files_format='jpeg', n_threads=16, cloud=False, overwrite=True)

    #XY SPLIT
    y = df[['target']]
    X = df.drop(columns=['target'])

    #VALIDATION SPLIT
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

    #FEATURE SELECTION
    print(X_train.columns)
    selected_features = ['sex', 'age', 'n_siblings_spouses', 'parch', 'fare', 'class', 'deck', 'embark_town', 'alone']
    X_train = X_train[selected_features]
    X_val = X_val[selected_features]
    X_test = X_test[selected_features]

    #CATEGORICAL NUMERICAL DETECTION
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
    numerical_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

    #FEATURE ENCODING
    target_encoder = TargetEncoder()
    X_train_encoded = target_encoder.fit_transform(X_train[categorical_features], y_train)
    X_val_encoded = target_encoder.transform(X_val[categorical_features])
    X_test_encoded = target_encoder.transform(X_test[categorical_features])
    for col in categorical_features:
        X_train[col] = X_train_encoded[col]
        X_val[col] = X_val_encoded[col]
        X_test[col] = X_test_encoded[col]

    #MISSINGS IMPUTATION
    imputer = SimpleImputer(strategy='median')
    X_train[numerical_features] = imputer.fit_transform(X_train[numerical_features])
    X_val[numerical_features] = imputer.transform(X_val[numerical_features])
    X_test[numerical_features] = imputer.transform(X_test[numerical_features])

    #STANDARD SCALING
    scaler = StandardScaler()
    X_train = pd.DataFrame(scaler.fit_transform(X_train),columns=X_train.columns,index=X_train.index)
    X_val = pd.DataFrame(scaler.transform(X_val), columns=X_val.columns, index=X_val.index)
    X_test = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns, index=X_test.index)

    def objective(trial):
        param = {
            'objective': 'binary',
            'metric': 'binary_logloss',
            'boosting_type': 'gbdt',
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
            'num_leaves': trial.suggest_int('num_leaves', 20, 150),
            'max_depth': trial.suggest_int('max_depth', 3, 15),
            'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 5, 100),
            'feature_fraction': trial.suggest_float('feature_fraction', 0.4, 1.0),
            'bagging_fraction': trial.suggest_float('bagging_fraction', 0.4, 1.0),
            'bagging_freq': trial.suggest_int('bagging_freq', 1, 10),
            'min_gain_to_split': trial.suggest_float('min_gain_to_split', 0.01, 0.3),
            'lambda_l1': trial.suggest_float('lambda_l1', 0.0, 10.0),
            'lambda_l2': trial.suggest_float('lambda_l2', 0.0, 10.0),
            'verbose': -1,
            'random_state': 42
        }

        train_data = lgb.Dataset(X_train, label=y_train)
        valid_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
        model = lgb.train(param, train_data, valid_sets=[valid_data], num_boost_round=1000)
        y_pred_proba = model.predict(X_val)
        return roc_auc_score(y_val, y_pred_proba)

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=50)

    best_params = study.best_params
    best_params['objective'] = 'binary'
    best_params['metric'] = 'binary_logloss'
    best_params['verbose'] = -1
    best_params['random_state'] = 42

    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
    model = lgb.train(best_params, train_data, valid_sets=[valid_data], num_boost_round=1000)

    y_test_pred_proba = model.predict(X_test)
    y_test_pred = (y_test_pred_proba > 0.5).astype(int)

    #METRICS
    test_accuracy = accuracy_score(y_test, y_test_pred)
    test_precision = precision_score(y_test, y_test_pred)
    test_recall = recall_score(y_test, y_test_pred)
    test_f1 = f1_score(y_test, y_test_pred)
    test_auc = roc_auc_score(y_test, y_test_pred_proba)

    test_metrics = {'accuracy': test_accuracy, 'precision': test_precision, 'recall': test_recall, 'f1': test_f1, 'auc': test_auc}
    print(test_metrics)

    #IMPORTANCES
    feature_importance = model.feature_importance()
    feature_importance_df = pd.DataFrame({'Feature': X_train.columns, 'Importance': feature_importance}).sort_values(by='Importance', ascending=False)
    print('Importances: ', feature_importance_df)

if __name__ == "__main__":
    main()