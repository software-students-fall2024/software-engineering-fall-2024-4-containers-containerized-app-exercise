FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

ADD . .

EXPOSE 5000

CMD ["python3","app.py"]