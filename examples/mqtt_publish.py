import logging
import random
import time

from rich.logging import RichHandler

from techflurry.controller.mqtt_client import MQTTClient

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger(__name__)

client = MQTTClient("127.0.0.1", "test/topic")
client.safe_connect()
while True:
    payload = random.uniform(6, 9)
    client.publish(
        topic=client.mqtt_topic, payload=payload, qos=0, retain=False
    )
    log.info(
        "New message in '%s' with payload %.2f ", client.mqtt_topic, payload
    )
    time.sleep(5)
