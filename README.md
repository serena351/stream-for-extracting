# ![Digital Futures](https://github.com/digital-futures-academy/DataScienceMasterResources/blob/main/Resources/datascience-notebook-header.png?raw=true)

## Setting Up Kafka Stream to Emit Random Numbers

This details how to set up a Kafka stream that emits random numbers at regular intervals. The stream is created using a Python script that acts as a Kafka producer, sending random numbers to a Kafka topic. The script is run in a Docker container on the same network as the Kafka broker, allowing it to communicate with the Kafka cluster.  Running this Docker network locally allows access to the Kafka broker via `localhost:9092` to consume the stream.

## Step 1: Set Up Kafka and Zookeeper Using Docker Compose

1. **Create a `docker-compose.yml` File**:
   Create a `docker-compose.yml` file with the following content:

```yaml
services:
    zookeeper:
        image: bitnami/zookeeper:latest
        ports:
            - "2181:2181"
        environment:
            - ALLOW_ANONYMOUS_LOGIN=yes
        networks:
            - kafka-network
    kafka:
        image: bitnami/kafka:latest
        ports:
            - "9092:9092"
        environment:
            - ALLOW_ANONYMOUS_LOGIN=yes
            - KAFKA_BROKER_ID=1
            - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
            - KAFKA_LISTENERS=INTERNAL://:9093,EXTERNAL://:9092
            - KAFKA_ADVERTISED_LISTENERS=INTERNAL://stream-for-extracting-kafka-1:9093,EXTERNAL://localhost:9092
            - KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
            - KAFKA_INTER_BROKER_LISTENER_NAME=INTERNAL
        depends_on:
            - zookeeper
        networks:
            - kafka-network
networks:
    kafka-network:
        driver: bridge
```

> ***NOTE***: The value of `KAFKA_ADVERTISED_LISTENERS` should be set to the name of the Kafka container followed by the port number `:9093`. This is the address that the producer script will use to connect to the Kafka broker. The `EXTERNAL` listener is set to `localhost:9092` to allow the console consumer to connect to the Kafka broker.  It is generally given the name of the folder the docker-compose file is in followed by the container name defined in the file and then suffixed with `-1`.

2. **Start Zookeeper and Kafka Using Docker Compose**:
   Navigate to the directory containing the docker-compose.yml file and run the following command to start Zookeeper and Kafka:

```sh
docker compose up -d
```

3. **Verify the Services are Running**:
   Check if the services are running by listing the Docker containers:

```sh
docker ps
```

4. **Create a Kafka Topic**:
   Run the following command to create a ***topic*** named `random_numbers`:

```sh
docker exec -it $(docker ps --filter "ancestor=bitnami/kafka" -q) kafka-topics.sh --create --topic random_numbers --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
```

---

## Step 2: Create and the Kafka Producer Script

1. **Create a Python Script**:
   Create a Python script named `kafka_producer.py` with the following content:

```python
import random
import time
from confluent_kafka import Producer

# Replace this with the name of your Kafka Container (leaving :9093 in place)
bootstrap_server = 'streams-kafka-1:9093' 

# Create a Kafka producer
producer = Producer({
    'bootstrap.servers': bootstrap_server,
    'request.timeout.ms': 25000,
    'retries': 10
})

# Function to generate and send a random number
def send_random_number():
    try:
        number = random.randint(1, 100)
        producer.produce('random_numbers', value=str(number).encode('utf-8'), callback=delivery_report)
        print(f'Sent: {number}')
    except Exception as e:
        print(f"Error sending message: {e}")

# Delivery report callback
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Main loop to emit a random number every 5 seconds
if __name__ == "__main__":
    try:
        while True:
            send_random_number()
            producer.poll(0)  # Serve delivery reports (callbacks)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopping producer")
    finally:
        producer.flush(10)
```

---

## Step 3: Create a Docker container to Run the Kafka Producer Script on the Network

1. **Create a `Dockerfile`**:
   Create a `Dockerfile` in the root of the project with the following content:

```Dockerfile
FROM python:3.13

WORKDIR /app

COPY kafka_producer.py /app/

RUN pip install confluent_kafka

CMD ["python", "kafka_producer.py"]
```

> This will create a Docker container with the Python:3.13 image, copy the `kafka_producer.py` script and install the `confluent_kafka` package.  It will not run the `kafka_producer.py` script.

3. **Build the Container**:
   Create the Docker container by running the following command:

```sh
docker build -t kafka_producer .
```

4. **Obtain the Docker Network name**:
   Run the following command to get the network name of the Kafka container:

```sh
docker network ls
```

5. **Run the Container**:
   Run the Docker container with the following command, which will execute the `kafka_producer.py` script:

```sh
docker run -it --network <network_name> kafka_producer
```

> You should replace `<network_name>` with the network name of the Kafka container obtained in the previous step.
> **Note**: Leave this script running to continuously emit random numbers to the Kafka topic. The script will print the value sent each time a random number is produced.

---

## Step 4: Verify the Stream of Numbers

1. **Consume Messages from the Kafka Topic**:
   Use the Kafka console consumer to see the random numbers being produced by opening another terminal and running the following command:

```sh
docker exec -it $(docker ps --filter "ancestor=bitnami/kafka" -q) kafka-console-consumer.sh --topic random_numbers --bootstrap-server 127.0.0.1:9092 --from-beginning
```

> It may take a couple of seconds for the stream to catch up with the producer script. You should see the random numbers being printed in the console.  These should match the numbers being sent by the producer script.

---

## Summary

1. Set up **Kafka** and **Zookeeper** using **Docker Compose** and create a **Kafka** *topic* named `random_numbers`.
2. Create a **Kafka** *producer* script that emits a random number every 5 seconds in a networked Docker container.
3. Run the container on the network to start emitting random numbers to the **Kafka** *topic*.
4. Use the **Kafka** console *consumer* to verify the stream of numbers.

By following these steps, you will have a Kafka stream that emits random numbers at regular intervals and logs the output to the terminal.
