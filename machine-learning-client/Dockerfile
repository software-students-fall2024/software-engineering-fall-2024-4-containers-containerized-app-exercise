FROM python:3.9

RUN pip install pipenv

COPY Pipfile ./
RUN pipenv lock --clear && cp Pipfile.lock Pipfile.lock

COPY Pipfile.lock ./
RUN pipenv install --system --deploy --dev

COPY . .

EXPOSE 5050

CMD ["flask", "run"]
