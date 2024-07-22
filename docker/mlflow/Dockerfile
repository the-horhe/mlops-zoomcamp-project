FROM python:3.12.4-slim-bullseye

RUN pip3 install mlflow

RUN mkdir /opt/mlflow
WORKDIR /opt/mlflow

CMD ["mlflow", "server", "--host", "0.0.0.0", "--backend-store-uri", "sqlite:////opt/mlflow/mlflow.db"]
