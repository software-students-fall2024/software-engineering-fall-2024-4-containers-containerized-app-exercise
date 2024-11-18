FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
COPY Pipfile /app/
COPY Pipfile.lock /app/

RUN pip install --no-cache-dir pipenv && pipenv install --system --deploy

COPY . /app/

EXPOSE 8000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

CMD ["flask", "run", "--port=8000"]
