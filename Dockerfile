# syntax=docker/dockerfile:1
FROM python:3.9-slim
WORKDIR /workspace
COPY . .
RUN pip install .
CMD [ "ssm" ]
