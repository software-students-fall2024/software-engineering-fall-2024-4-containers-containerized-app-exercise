FROM python:3.10-slim

WORKDIR /app
WORKDIR /app

COPY Pipfile Pipfile.lock ./
COPY .env /app/.env

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

COPY . .

CMD ["python3", "app.py"]