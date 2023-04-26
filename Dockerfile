FROM python:3.8.6-slim

ENV PYTHONUNBUFFERED 1 
EXPOSE 8080
WORKDIR /app

COPY ./requirements.txt .
COPY ./src ./src

RUN pip install -r requirements.txt

CMD ["python", "start.py"]

