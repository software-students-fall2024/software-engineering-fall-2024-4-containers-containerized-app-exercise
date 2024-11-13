
FROM python:3.12-slim

# install dependencies
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

# copy code 
COPY . .
CMD ["python", "app.py"]