import random
import time
from confluent_kafka import Producer

# Replace this with the name of your Kafka Container (leaving :9093 in place)
bootstrap_server = 'stream-for-extracting-kafka-1:9093' 

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
