FROM python:3.9

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY . .

EXPOSE 5050

CMD ["flask", "run", "--host=0.0.0.0", "--port=5050"]
