import urllib.parse

import simplejson as json
import redis

from gemstone.event.transport.base import BaseEventTransport


class RedisEventTransport(BaseEventTransport):
    def __init__(self, redis_url):
        super(RedisEventTransport, self).__init__()
        conn_details = urllib.parse.urlparse(redis_url)
        if conn_details.scheme not in ("redis", "rediss", "unix"):
            raise ValueError(
                "Invalid redis url: scheme '{}' not allowed".format(conn_details.scheme))

        self.connection_pool = redis.ConnectionPool.from_url(redis_url)
        self.handlers = {}

    def get_pubsub(self):
        conn = self.get_redis_connection()
        pubsub = conn.pubsub(ignore_subscribe_messages=True)
        return pubsub

    def get_redis_connection(self):
        return redis.StrictRedis(connection_pool=self.connection_pool)

    def start_accepting_events(self):
        pubsub = self.get_pubsub()
        pubsub.subscribe(*tuple(self.handlers.keys()))

        for message in pubsub.listen():
            event_name = message["channel"].decode()
            event_data = message["data"].decode()

            self.on_event_received(event_name, json.loads(event_data))

    def register_event_handler(self, handler_func, handled_event_name):
        self.handlers[handled_event_name] = handler_func

    def emit_event(self, event_name, event_body):
        conn = self.get_redis_connection()
        conn.publish(event_name, json.dumps(event_body))

    def on_event_received(self, event_name, event_body):
        handler = self.handlers.get(event_name, None)
        if not handler:
            return
        self.run_on_main_thread(handler, (event_body,), {})
