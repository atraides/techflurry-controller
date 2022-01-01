import logging

from rich.logging import RichHandler

from techflurry.controller.mqtt_client import MQTTClient

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

client = MQTTClient("127.0.0.1", "test/topic")
client.safe_connect()
client.loop_forever()
