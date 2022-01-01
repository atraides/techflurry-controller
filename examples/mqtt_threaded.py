import logging
import random
from signal import SIGHUP, SIGINT, SIGTERM, signal
from threading import Event, Thread
from typing import List

from rich.logging import RichHandler

from techflurry.controller.mqtt_client import MQTTClient

log = logging.getLogger(__name__)

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

THREADS: List[Thread] = []
STOP_EVENT: Event = Event()
MQTT_CLIENT: MQTTClient = MQTTClient(topic="test/#")


def graceful_exit():
    log.debug("Graceful shutdown")
    STOP_EVENT.set()
    MQTT_CLIENT.shutdown()
    stop_sensors()


def signal_catcher(signal_number, frame):
    if signal_number == SIGTERM:
        log.info("SIGTERM received! Quitting.")
        graceful_exit()
    if signal_number == SIGHUP:
        log.info("SIGHUP received. Restarting.")
    if signal_number == SIGINT:
        log.info("SIGINT received. Quitting.")
        graceful_exit()


def stop_sensors():
    for thread in THREADS:
        log.debug("Stopping thread '%s'", thread.name)
        thread.join()
    log.debug("All sensors stopped")


def start_sensor(
    exit_event: Thread,
    mqtt_topic: str = None,
    payload_min: int = 6,
    payload_max: int = 10,
):
    client = MQTTClient()
    client.safe_connect("localhost")
    while not exit_event.is_set():
        payload = random.uniform(payload_min, payload_max)
        client.publish(topic=mqtt_topic, payload=payload)
        exit_event.wait(5)


if __name__ == "__main__":

    signal(SIGTERM, signal_catcher)
    signal(SIGHUP, signal_catcher)
    signal(SIGINT, signal_catcher)

    for i in range(1, 6):
        log.debug("Starting thread 'Thread-%d'", i)
        thread = Thread(
            target=start_sensor,
            args=(
                STOP_EVENT,
                f"test/topic-{i}",
                5 * i,
                10 * i,
            ),
        )
        thread.start()
        THREADS.append(thread)

    # both threads completely executed
    MQTT_CLIENT.safe_connect("localhost")
    MQTT_CLIENT.loop_start()
    # graceful_exit()

# mqtt_topic = "test/topic"

# client = MQTTClient()
# client.safe_connect("localhost")
# while True:
#     payload = random.uniform(6, 9)
#     client.publish(topic=mqtt_topic, payload=payload, qos=0, retain=False)
#     log.info("Publishing to '%s' with payload %.2f ", mqtt_topic, payload)
#     time.sleep(5)
