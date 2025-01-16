from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import optuna
import mlflow
import pandas as pd

class MLPipeline:
    def __init__(self):
        self.pipeline = self._create_pipeline()
        mlflow.set_tracking_uri("http://localhost:5000")
        self.study = optuna.create_study(direction="maximize")

    def _create_pipeline(self):
        return Pipeline([
            ('scaler', StandardScaler()),
            ('feature_selection', SelectKBest(score_func=f_classif)),
            ('classifier', RandomForestClassifier())
        ])

    def train(self, X, y):
        with mlflow.start_run():
            self.study.optimize(lambda trial: self._objective(trial, X, y), n_trials=100)
            best_params = self.study.best_params
            self.pipeline.set_params(**best_params)
            self.pipeline.fit(X, y)
            mlflow.log_params(best_params)
            mlflow.sklearn.log_model(self.pipeline, "model")

    def _objective(self, trial, X, y):
        params = {
            'classifier__n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'classifier__max_depth': trial.suggest_int('max_depth', 3, 10),
            'feature_selection__k': trial.suggest_int('k', 5, X.shape[1])
        }
        self.pipeline.set_params(**params)
        return cross_val_score(self.pipeline, X, y, cv=5).mean() 