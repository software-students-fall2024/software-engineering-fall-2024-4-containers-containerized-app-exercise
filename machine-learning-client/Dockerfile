FROM python:3.10-slim

WORKDIR /app

COPY Pipfile Pipfile.lock requirements.txt /app/

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

COPY . /app

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
