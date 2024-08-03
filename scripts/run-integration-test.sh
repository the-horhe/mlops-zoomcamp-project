#!/usr/bin/env bash

set -uoe pipefail

# Prepare sandbox environment
bash scripts/run-sandbox.sh --with-service

# Run training  pipeline
export DP_DATA_PATH="tests/data/data_sample_integration.csv"
dagster job execute -f src/pipelines/jobs.py -j train_linear_model

# Register model
python3 tests/utils/register_latest_model.py

# Rester service to reload model
docker-compose -f docker/docker-compose-service.yaml restart prediction-service
# TODO: replace with healthcheck
sleep 10  # service need some time to start and load model

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
