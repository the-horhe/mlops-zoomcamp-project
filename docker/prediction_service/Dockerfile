FROM python:3.10.14-slim-bullseye

RUN apt-get update && apt-get install -y curl nano

RUN mkdir /opt/prediction_service
WORKDIR /opt/prediction_service

COPY docker/prediction_service/requirements.txt .
RUN pip install -r requirements.txt

COPY src/web-service .

# -u flag is for unbuffered otput to stdout to see log in docker logs command
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0", "lin_reg_service:app"]
