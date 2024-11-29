FROM python:3.13

WORKDIR /app

COPY kafka_producer.py /app/

RUN pip install confluent_kafka

CMD ["python", "kafka_producer.py"]