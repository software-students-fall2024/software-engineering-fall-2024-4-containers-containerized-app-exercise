FROM python:3.10-slim

WORKDIR /

COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir pipenv && \
    pipenv install --deploy --ignore-pipfile

COPY . .

CMD ["pipenv", "run", "python", "app.py"]
