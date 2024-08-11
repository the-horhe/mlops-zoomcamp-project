#!/usr/bin/env bash

set -uoe pipefail


COMPOSE_FILES=" -f docker/docker-compose.yaml "
while [ "${1-}" != "" ]; do
    case $1 in
        --with-service )
          shift
          COMPOSE_FILES="$COMPOSE_FILES -f docker/docker-compose-service.yaml"
        ;;
        --stop )
          shift
          docker compose $COMPOSE_FILES stop
          exit 0
        ;;
    esac
done

# Docker-compose
docker compose $COMPOSE_FILES stop
docker compose $COMPOSE_FILES up --build -d --wait

# Create localstack bucket
## Setup minio client - add sandbox config
docker compose $COMPOSE_FILES exec s3 bash -c "mc config host add sandbox http://localhost:9000 minioadmin minioadmin"
## Add bucket using sandbox config
docker compose $COMPOSE_FILES exec s3 bash -c "mc mb -p sandbox/test-localstack-bucket"


# TODO: print services links
