#!/usr/bin/env bash

set -uoe pipefail

# Docker-compose
docker-compose -f docker/docker-compose.yaml stop
docker-compose -f docker/docker-compose.yaml up --build -d

# TODO: print services links
