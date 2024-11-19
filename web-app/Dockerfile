FROM python:3.10-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./
COPY .env /app/.env


RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

COPY . .

EXPOSE 8000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]
