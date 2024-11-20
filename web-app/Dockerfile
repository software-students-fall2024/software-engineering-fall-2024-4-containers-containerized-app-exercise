FROM python:3.10

WORKDIR /app

COPY . /app

RUN pipenv install

EXPOSE 1001

CMD ["python", "app.py"]