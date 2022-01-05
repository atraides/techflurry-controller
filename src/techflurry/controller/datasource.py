# -*- coding: utf-8 -*-

"""TechFlurry Datasource."""

# MIT License (see LICENSE)
# Author: Dániel Hagyárossy <d.hagyarossy@sapstar.eu>
# Author: László Béres <laszloberes@hotmail.hu>


from techflurry.controller.mqtt_client import MQTTClient


class TFDataSource:
    def __init__(self, topic="#", hostname="localhost") -> None:
        self.hostname = hostname
        self.topic = topic
        self.client = MQTTClient(topic=self.topic)

        self._data_value = None

    @property
    def data_value(self):
        return self._data_value

    def start(self):
        def on_message_save(client, userdata, msg):
            self._data_value = msg.payload

        self.client.on_message = on_message_save
        self.client.safe_connect(self.hostname)
        self.client.loop_start()

    def stop(self):
        self.client.shutdown()
