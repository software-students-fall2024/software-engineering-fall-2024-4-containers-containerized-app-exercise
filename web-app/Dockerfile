FROM python:3.10-slim-buster

WORKDIR /app

COPY . /app

RUN pip install pipenv
RUN pipenv install
RUN apt-get update && apt-get install -y ffmpeg

ADD . .

EXPOSE 5000

CMD ["pipenv","run","python3","app.py","--host=0.0.0.0"]