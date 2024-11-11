FROM python:3.13

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

COPY . .

ARG MONGO_CXN_STRING
ARG ML_CLIENT_PORT

EXPOSE 5001

CMD ["python", "app.py"]