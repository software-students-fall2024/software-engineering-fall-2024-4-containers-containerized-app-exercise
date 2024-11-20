FROM python:3.9-slim

WORKDIR /machine-learning-client

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
