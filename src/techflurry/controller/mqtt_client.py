∑# -*- coding: utf-8 -*-

"""TechFlurry MQTT Client module."""

# MIT License (see LICENSE)
# Author: Dániel Hagyárossy <d.hagyarossy@sapstar.eu>
# Author: László Béres <laszloberes@hotmail.hu>

import time

from paho.mqtt.client import Client, MQTTv5

from techflurry.controller.errors.connection import TFConnectionFailed
from techflurry.controller.logger import tflog


class MQTTClient(Client):
    """TechFlurry MQTT client class definition.

    Methods:
        __init__(self, protocol, **kwargs):

    """

    def __init__(self, hostname, topic=None, protocol=MQTTv5, **kwargs):
        """Initialize the TechFlurry MQTT client.

        Args:
            protocol: MQTT protocol version. Default is MQTTv5.

        """

        super(MQTTClient, self).__init__(protocol=protocol, **kwargs)

        self.last_pub_time = time.time()
        # self.topic_ack: List[str] = [] # http://www.steves-internet-guide.com/client-objects-python-mqtt/
        self.run_flag = True
        self.subscribe_flag = False
        self.bad_connection_flag = False
        self.connected_flag = False
        self.disconnect_flag = False
        self.disconnect_time = 0.0
        self.pub_msg_count = 0
        # self.devices: List[str] = []
        self.hostname = hostname
        self.mqtt_topic = topic

    def on_connect(self, client, userdata, flags, rc, *arg):
        while not self.connected_flag:
            if rc.value == 0:
                self.connected_flag = True  # set flag
                tflog.info("MQTT connection successful.")
                tflog.info("Subscribing to topic: %s", self.mqtt_topic)
                self.subscribe(self.mqtt_topic)
            else:
                raise TFConnectionFailed(rc.value)

    def on_message(self, client, userdata, msg):
        payload: float = 0.0
        if hasattr(msg, "payload"):
            payload = float(
                msg.payload
            )  # @TODO: Fail when trying to convert a non number.

        tflog.info(
            "New message in '%s' with payload %.2f ", msg.topic, payload
        )

    def shutdown(self):
        tflog.debug("Stopping the loop.")
        self.loop_stop
        tflog.debug("Disconnecting from the broker.")
        self.disconnect()

    def safe_connect(self, retry=60, max_retries=5):
        current_retry = 1

        while True:
            try:
                tflog.info("Connecting to %s.", self.hostname)
                self.connect(self.hostname)
                break
            except OSError as error:
                if error.errno == 113:  # No route to host
                    tflog.warning(
                        "Can't connect to the MQTT broker (No route to host)."
                    )
                    tflog.warning(
                        "MQTT connection failed. Retrying in %s seconds.",
                        retry,
                    )

                    time.sleep(retry)
                    if max_retries and current_retry >= max_retries:
                        raise
                    current_retry = current_retry + 1
                else:
                    raise
