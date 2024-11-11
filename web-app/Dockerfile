FROM python:3.10-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --deploy --ignore-pipfile

COPY . .

CMD ["python", "web-app.py"]