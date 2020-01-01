FROM python:3.8-alpine

WORKDIR /srv/flake8-check-action
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN pip install .
ENTRYPOINT python -m flake8_check_action
