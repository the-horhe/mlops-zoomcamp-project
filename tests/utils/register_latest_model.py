import os

import mlflow
from flask import Flask
from mlflow.entities.experiment import Experiment
from mlflow.entities.run import Run
from mlflow.tracking import MlflowClient

mlflow_url = os.environ.get("DP_MLFLOW_URL", "http://127.0.0.1:5000")
model_name = os.environ.get("DP_MLFLOW_MODEL_NAME", "drought-prediction-test")
experiment_name = os.environ.get("DP_MLFLOW_EXPERIMENT_NAME", "weather-prediction-exp")

app = Flask(__name__)


client = MlflowClient(mlflow_url)
mlflow.set_tracking_uri(mlflow_url)


experiment: Experiment = client.get_experiment_by_name(experiment_name)
latest_run: Run = client.search_runs(
    experiment_ids=experiment.experiment_id,
    max_results=1,
)[0]

run_id = latest_run.info.run_id

mlflow.register_model(
    model_uri=f"runs:/{run_id}/model",
    name=model_name,
)
