import logging

from rich.logging import RichHandler

from techflurry.controller.mqtt_client import MQTTClient

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

mqtt_topic = "test/topic"

client = MQTTClient(topic=mqtt_topic)
client.safe_connect("localhost")
client.loop_forever()
