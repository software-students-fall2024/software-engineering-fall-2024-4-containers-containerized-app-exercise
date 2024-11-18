FROM python:3.10-slim

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN pip install --no-cache-dir pipenv && \
    pipenv install --deploy --ignore-pipfile

COPY . /app/

# entry point
CMD ["pipenv", "run", "python", "app.py"]  
