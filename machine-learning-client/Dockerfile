FROM python:3.10

RUN pip install pipenv

# Set the working directory inside the container
WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN pipenv install --system --deploy

COPY . /app

EXPOSE 5050

CMD ["flask", "run", "--host=0.0.0.0", "--port=5050"]
