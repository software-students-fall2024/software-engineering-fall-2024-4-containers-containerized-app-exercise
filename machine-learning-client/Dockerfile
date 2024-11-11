FROM python:3.10

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

COPY . .

EXPOSE 5002

CMD ["python", "app.py"]