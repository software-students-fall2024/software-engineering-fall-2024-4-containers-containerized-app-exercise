FROM python:3.8-slim-buster

WORKDIR /machine-learning-client

RUN pip install pipenv
COPY Pipfile .
# RUN pipenv install

ADD . .

CMD ["python3", "ml_client.py"]
