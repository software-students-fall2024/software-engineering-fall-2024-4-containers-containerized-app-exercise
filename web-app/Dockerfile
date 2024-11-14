FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV AUDIO_DIR=/app/audio

CMD ["python", "app.py"]
