FROM python:3.9

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy --dev

COPY . .

EXPOSE 5050

CMD ["flask", "run"]
