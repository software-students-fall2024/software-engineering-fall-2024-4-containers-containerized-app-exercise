FROM python:3.8-slim-buster

WORKDIR /machine-learning-client

RUN pip install pipenv
COPY requirements.txt .
RUN pip install --trusted-host pypi.python.org -r requirements.txt
# RUN pipenv install

ADD . .

CMD ["python3", "ml_client.py"]
