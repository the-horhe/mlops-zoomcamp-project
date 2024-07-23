import mlflow
import numpy as np
from flask import Flask, Response, jsonify, request
from mlflow.entities.model_registry.registered_model import RegisteredModel
from mlflow.pyfunc import PyFuncModel
from mlflow.tracking import MlflowClient

# TODO: hos as parameter
mlflow_url = "http://127.0.0.1:5000"
model_name = "drought-prediction"

app = Flask(__name__)


def _load_registry_model() -> PyFuncModel:
    client = MlflowClient(mlflow_url)
    mlflow.set_tracking_uri(mlflow_url)

    res: list[RegisteredModel] = client.search_registered_models(
        filter_string=f"name='{model_name}'",
    )

    if len(res) <= 0:
        raise RuntimeError(
            f"Model {model_name} not found in model registry. " "Considers register model first."
        )

    run_id = res[0].latest_versions[0].run_id

    loaded_model: PyFuncModel = mlflow.pyfunc.load_model(f"runs:/{run_id}/models")

    return loaded_model


@app.route("/predict", methods=["POST"])
def predict() -> Response:
    data = request.json
    if not isinstance(data, dict):
        raise ValueError(rf"Invalid request: {data}, expected \{'lag_365': [values]\}")

    lag_365 = np.array(data["lag_365"]).reshape(-1, 1)

    prediction = model.predict(lag_365)

    return jsonify({"predictions": prediction.tolist()})


if __name__ == "__main__":
    model = _load_registry_model()
    app.run(debug=True, host="0.0.0.0", port=9696)
