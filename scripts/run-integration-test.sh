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
# TODO: start only web-service container, but with health status await
docker compose -f docker/docker-compose-service.yaml up --build -d --wait

# Get prediction
prediction=$(curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"lag_365": [0]}')

# Check results
expected_prediction='{"predictions":[16.362569259476018]}'
if [ "$prediction" != $expected_prediction ]; then
  echo "Invalid prediction: {expected_prediction}"
  bash -c "scripts/run-sandbox.sh --with-service --stop"
  exit 1
fi

echo "Test passed! You are awesome!"

# Teardown sandbox
bash -c "scripts/run-sandbox.sh --with-service --stop"
