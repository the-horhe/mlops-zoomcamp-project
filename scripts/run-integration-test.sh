#!/usr/bin/env bash

set -uoe pipefail

# Prepare sandbox environment
bash scripts/run-sandbox.sh

# Run training  pipeline
export DP_DATA_PATH="tests/data/data_sample_integration.csv"
poetry run dagster job execute -f src/pipelines/jobs.py -j train_linear_model

# Register model
poetry run python3 tests/utils/register_latest_model.py

# Restart service to reload model
# TODO: restart only web-service container, but with health status await
bash scripts/run-sandbox.sh --stop

export DP_MLFLOW_MODEL_NAME="drought-prediction-test"
bash scripts/run-sandbox.sh --with-service


# Get prediction
prediction=$(curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"lag_365": [0]}')

# Check results
expected_prediction='{"predictions":[14.350989815313053]}'
if [ "$prediction" != $expected_prediction ]; then
  echo "Invalid prediction: $expected_prediction"
  bash -c "scripts/run-sandbox.sh --with-service --stop"
  exit 1
fi

echo "Test passed! You are awesome!"

# Teardown sandbox
bash -c "scripts/run-sandbox.sh --with-service --stop"
