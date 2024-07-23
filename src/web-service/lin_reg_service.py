import os

import mlflow
import numpy as np
from flask import Flask, Response, jsonify, request
from mlflow.entities.model_registry.registered_model import RegisteredModel
from mlflow.pyfunc import PyFuncModel
from mlflow.tracking import MlflowClient

mlflow_url = os.environ.get("DP_MLFLOW_URL", "http://127.0.0.1:5000")
model_name = os.environ.get("DP_MLFLOW_MODEL_NAME", "drought-prediction")

app = Flask(__name__)


client = MlflowClient(mlflow_url)
mlflow.set_tracking_uri(mlflow_url)

res: list[RegisteredModel] = client.search_registered_models(
    filter_string=f"name='{model_name}'",
)

if len(res) <= 0:
    raise RuntimeError(
        f"Model {model_name} not found in model registry {mlflow_url}. "
        "Considers register model first."
    )

run_id = res[0].latest_versions[0].run_id

loaded_model: PyFuncModel = mlflow.pyfunc.load_model(f"runs:/{run_id}/models")


@app.route("/predict", methods=["POST"])
def predict() -> Response:
    data = request.json
    if not isinstance(data, dict):
        raise ValueError(rf"Invalid request: {data}, expected \{'lag_365': [values]\}")

    lag_365 = np.array(data["lag_365"]).reshape(-1, 1)

    prediction = loaded_model.predict(lag_365)

    return jsonify({"predictions": prediction.tolist()})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
