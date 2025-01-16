from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import GradientBoostingRegressor
import optuna
import mlflow
import numpy as np

class ModelOptimizer:
    def __init__(self):
        self.study = optuna.create_study(direction="minimize")
        self.best_models = {}
        self.performance_history = []
        mlflow.set_tracking_uri("http://localhost:5000")

    async def optimize_models(self):
        try:
            # Optimize each model type
            model_types = ['performance', 'anomaly', 'prediction']
            for model_type in model_types:
                with mlflow.start_run(run_name=f"optimize_{model_type}"):
                    best_model = await self._optimize_model(model_type)
                    self.best_models[model_type] = best_model
                    
                    # Log metrics and parameters
                    mlflow.log_params(best_model.get_params())
                    mlflow.log_metrics(self._evaluate_model(best_model))
                    
                    # Save model
                    mlflow.sklearn.log_model(best_model, f"{model_type}_model")

            return {
                'status': 'success',
                'optimized_models': list(self.best_models.keys()),
                'performance_metrics': self._get_performance_metrics()
            }
        except Exception as e:
            logger.error(f"Model optimization error: {str(e)}")
            return None

    def _optimize_model(self, model_type):
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_loguniform('learning_rate', 1e-4, 1e-1),
                'subsample': trial.suggest_uniform('subsample', 0.6, 1.0)
            }
            
            model = GradientBoostingRegressor(**params)
            model.fit(self.X_train, self.y_train)
            return self._calculate_objective(model)

        self.study.optimize(objective, n_trials=100)
        return self._build_optimized_model(self.study.best_params) 