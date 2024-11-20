FROM python:3.10-slim

WORKDIR /

COPY Pipfile Pipfile.lock ./

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

RUN pip install --no-cache-dir pipenv && \
    pipenv install --deploy --ignore-pipfile

COPY . .

# Entry point
CMD ["pipenv", "run", "python", "app.py"]