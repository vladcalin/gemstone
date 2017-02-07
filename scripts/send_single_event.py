import random
import json
import pika
import time

def pack_message(msg):
    return json.dumps(msg)

i = 0

while True:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="192.168.1.71",
            credentials=pika.PlainCredentials(username="admin", password="X5f6rPmx1yYz")
        )
    )


    channel = connection.channel()


    channel.basic_publish(
            exchange="gemstone.events.event_{}".format(random.choice(["one", "two"])),
            routing_key='',
            body=pack_message({"username": "vlad", "email": "vlad_calin@swag.ro", "tags": ["awesome", "programmer"], "age": 21})
        )
    connection.close()
    i += 1
    print(i)

    time.sleep(0.25)
