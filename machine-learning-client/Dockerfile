FROM python:3.10-slim

WORKDIR /app

COPY Pipfile Pipfile.lock requirements.txt /app/

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

ADD . .

EXPOSE 5000

CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]