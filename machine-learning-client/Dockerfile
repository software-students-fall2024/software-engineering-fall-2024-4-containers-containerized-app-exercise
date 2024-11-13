
FROM python:3.8-slim-buster

WORKDIR /app


RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt ./
COPY training_data ./training_data


RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python3", "main.py"]
