FROM python:3.10-slim

WORKDIR /app
WORKDIR /app

COPY Pipfile Pipfile.lock ./
COPY .env /app/.env

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

COPY . .

ENV GOOGLE_API_KEY=$GOOGLE_API_KEY
ENV MONGO_URI=$MONGO_URI
ENV SECRET_KEY=$SECRET_KEY

CMD ["python3", "app.py"]