# syntax=docker/dockerfile:1
FROM python:3.7-slim
WORKDIR /workspace
COPY . .
RUN pip install -e .
CMD [ "ssm" ]
