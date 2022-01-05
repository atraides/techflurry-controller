import logging
from signal import SIGHUP, SIGINT, SIGTERM, signal
from threading import Event

# from rich import inspect
from rich.logging import RichHandler

from techflurry.controller.datasource import TFDataSource

log = logging.getLogger(__name__)
FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
datasource = TFDataSource(topic="test_topic")
STOP_EVENT: Event = Event()


def graceful_exit():
    log.debug("Graceful shutdown")
    datasource.stop()
    STOP_EVENT.set()


def signal_catcher(signal_number, frame):
    if signal_number == SIGTERM:
        log.info("SIGTERM received! Quitting.")
        graceful_exit()
    if signal_number == SIGHUP:
        log.info("SIGHUP received. Restarting.")
    if signal_number == SIGINT:
        log.info("SIGINT received. Quitting.")
        graceful_exit()


if __name__ == "__main__":

    signal(SIGTERM, signal_catcher)
    signal(SIGHUP, signal_catcher)
    signal(SIGINT, signal_catcher)

    datasource.start()

    while not STOP_EVENT.is_set():
        log.info("DataSource value is %s", datasource.data_value)
        STOP_EVENT.wait(10)
