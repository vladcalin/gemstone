import pika

if __name__ == '__main__':
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="192.168.1.71",
            credentials=pika.PlainCredentials(username="admin", password="X5f6rPmx1yYz")
        )
    )
    channel = connection.channel()

    for _ in range(100):
        channel.basic_publish(
            exchange="gemstone.events.event_one",
            routing_key='',
            body="How you doin' ?"
        )
    connection.close()
