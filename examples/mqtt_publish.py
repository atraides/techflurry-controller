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

mqtt_topic = "test/topic"

client = MQTTClient()
client.safe_connect("localhost")
while True:
    payload = random.uniform(6, 9)
    client.publish(topic=mqtt_topic, payload=payload, qos=0, retain=False)
    log.info("Publishing to '%s' with payload %.2f ", mqtt_topic, payload)
    time.sleep(5)
