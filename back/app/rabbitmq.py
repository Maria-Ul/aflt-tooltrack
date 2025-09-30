import pika
from .config import RABBITMQ_URL

def send_message(message):
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue='my_queue')  # Объявляем очередь

        channel.basic_publish(exchange='', routing_key='my_queue', body=message)
        print(f" [x] Sent '{message}'")
        connection.close()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}")
