# syntax=docker/dockerfile:1
FROM python
LABEL version="1.0" maintainer="admin@example.com"
WORKDIR /workspace
COPY . .
ENV FOO='BAR'
#CMD [ "python3", "app.py" ]