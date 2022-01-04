import logging

import pytest
from paho.mqtt.client import MQTTMessage
from paho.mqtt.reasoncodes import ReasonCodes

from techflurry.controller.errors.connection import TFConnectionFailed
from techflurry.controller.mqtt_client import MQTTClient


@pytest.fixture()
def mqtt_client():
    client = MQTTClient("subscribed/topic")
    return client


@pytest.fixture()
def mqtt_test_topic():
    return "test/topic"


@pytest.fixture()
def mqtt_client_no_topic():
    client = MQTTClient()
    return client


class MockMQTTBroker:
    def __init__(self, on_connect=None, on_disconnect=None):
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self.dc_code = 0
        self.reason_code = ReasonCodes(2)  # Success

    @property
    def on_connect(self):
        if self._on_connect:  # pragma: no cover
            return self._on_connect

    @property
    def on_disconnect(self):
        if self._on_disconnect:  # pragma: no cover
            return self._on_disconnect

    def mock_connect(self, hostname):
        if callable(self.on_connect):  # pragma: no cover
            self.on_connect("", None, {"flag": "data"}, self.reason_code)

    def mock_disconnect(self, reasoncode=None, properties=None):
        if callable(self.on_disconnect):  # pragma: no cover
            self.on_disconnect("", None, self.dc_code, None)


def mock_os_error(_):
    raise OSError(2, "No such file or directory", "foo")


def mock_no_route_to_host(_):
    raise OSError(113, "No route to host", "foo")


class TestBasicFunctions:
    def test_initiate_mqtt_client(self, mqtt_client):
        assert isinstance(mqtt_client, MQTTClient)

    def test_mqtt_client_connection_to_server(self, mqtt_client, monkeypatch):
        mqtt_broker = MockMQTTBroker(on_connect=mqtt_client.on_connect)
        monkeypatch.setattr(mqtt_client, "connect", mqtt_broker.mock_connect)
        mqtt_client.safe_connect("invalid.hostname.local")

        assert mqtt_client.connected_flag is True

    def test_mqtt_client_disconnection_from_server(self, mqtt_client, caplog):
        caplog.set_level(logging.INFO)
        mqtt_client.on_disconnect("", None, 0, None)
        assert len(caplog.records) == 1
        assert mqtt_client.disconnect_flag is True

    def test_mqtt_client_shutdown(self, mqtt_client, monkeypatch):
        mqtt_broker = MockMQTTBroker(on_disconnect=mqtt_client.on_disconnect)
        monkeypatch.setattr(
            mqtt_client, "disconnect", mqtt_broker.mock_disconnect
        )
        mqtt_client.shutdown()
        assert mqtt_client.disconnect_flag is True

    def test_mqtt_client_connection_without_topic(
        self, mqtt_client_no_topic, monkeypatch
    ):
        mqtt_client = mqtt_client_no_topic
        mqtt_broker = MockMQTTBroker(on_connect=mqtt_client.on_connect)
        monkeypatch.setattr(mqtt_client, "connect", mqtt_broker.mock_connect)
        mqtt_client.safe_connect("invalid.hostname.local")

        assert mqtt_client.connected_flag is True

    def test_log_incoming_messages(self, mqtt_client, mqtt_test_topic, caplog):
        caplog.set_level(logging.INFO)
        message = MQTTMessage(topic=bytes(mqtt_test_topic, "utf-8"))
        message.payload = b"12"
        mqtt_client.on_message("", None, message)

        record = caplog.records[0]
        assert mqtt_test_topic in record.message
        assert record.funcName == "message_function"

    def test_log_non_numeric_messages(
        self,
        mqtt_client,
        mqtt_test_topic,
        caplog,
    ):
        caplog.set_level(logging.INFO)
        message = MQTTMessage(topic=bytes(mqtt_test_topic, "utf-8"))
        message.payload = b"test"
        mqtt_client.on_message("", None, message)

        record = caplog.records[0]
        assert mqtt_test_topic in record.message
        assert record.funcName == "message_function"

    def test_dont_log_incoming_messages_without_payload(
        self,
        mqtt_client,
        mqtt_test_topic,
        caplog,
    ):
        caplog.set_level(logging.INFO)
        message = MQTTMessage(topic=bytes(mqtt_test_topic, "utf-8"))
        mqtt_client.on_message("", None, message)

        print(caplog.records)
        assert len(caplog.records) == 0


class TestErrorHandling:
    def test_mqtt_client_connection_to_server_fail(
        self,
        mqtt_client,
        monkeypatch,
    ):
        mqtt_broker = MockMQTTBroker(on_connect=mqtt_client.on_connect)
        monkeypatch.setattr(mqtt_client, "connect", mqtt_broker.mock_connect)
        monkeypatch.setattr(
            mqtt_broker,
            "reason_code",
            ReasonCodes(2, identifier=135),  # 135: "Not authorized"
        )
        with pytest.raises(TFConnectionFailed) as error:
            mqtt_client.safe_connect("invalid.hostname.local")

        error_value = error.value
        assert "TFConnectionFailed" in str(error_value)
        assert isinstance(error_value, TFConnectionFailed)
        assert error_value.rc == 135

    def test_mqtt_connect_without_host_fails(self, mqtt_client):
        with pytest.raises(TypeError):
            mqtt_client.safe_connect()

    def test_mqtt_client_fail_with_no_route_to_host(
        self, mqtt_client, monkeypatch
    ):
        monkeypatch.setattr(mqtt_client, "connect", mock_no_route_to_host)

        with pytest.raises(OSError) as error:
            mqtt_client.safe_connect(
                "invalid.hostname.local", retry=1, max_retries=2
            )

        error_value = error.value
        assert error_value.errno == 113

    def test_mqtt_client_fail_with_generic_os_error(
        self, mqtt_client, monkeypatch
    ):
        monkeypatch.setattr(mqtt_client, "connect", mock_os_error)

        with pytest.raises(OSError) as error:
            mqtt_client.safe_connect("invalid.hostname.local")

        error_value = error.value
        assert error_value.errno == 2

    def test_mqtt_client_disconnect_from_server_fails(self, mqtt_client):
        mqtt_client.on_disconnect("", None, 10, None)
        assert mqtt_client.disconnect_flag is False
