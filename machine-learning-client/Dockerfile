FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install pipenv
RUN pipenv install
RUN apt-get update && apt-get install -y flac

CMD ["pipenv", "run", "python", "app.py"]