FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install pipenv
RUN pipenv install

CMD ["pipenv", "run", "python", "app.py"]