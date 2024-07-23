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
          docker-compose $COMPOSE_FILES stop
          exit 0
        ;;
    esac
done

# Docker-compose
docker-compose $COMPOSE_FILES stop
docker-compose $COMPOSE_FILES up --build -d

# TODO: print services links
