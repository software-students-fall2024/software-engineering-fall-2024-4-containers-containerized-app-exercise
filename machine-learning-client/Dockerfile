FROM python:3.12-slim

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN pip install pipenv

RUN pipenv install --deploy --ignore-pipfile

COPY . /app/

# entry point
CMD ["pipenv", "run", "python", "app.py"]  