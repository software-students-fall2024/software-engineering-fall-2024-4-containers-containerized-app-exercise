FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY . .

CMD ["python", "main.py"]
