import pytest
from paho.mqtt.reasoncodes import ReasonCodes

from techflurry.controller.errors.connection import TFConnectionFailed
from techflurry.controller.mqtt_client import MQTTClient


@pytest.fixture()
def mqtt_client():
    client = MQTTClient("invalid.domain.local", "subscribed/topic")
    return client


class MockMQTTBroker:
    def __init__(self, on_connect=None):
        self._on_connect = on_connect
        self.reason_code = ReasonCodes(2)  # Success

    @property
    def on_connect(self):
        if self._on_connect:
            return self._on_connect

    def mock_connect(self, hostname):
        if callable(self.on_connect):
            self.on_connect("", None, {"flag": "data"}, self.reason_code)


def mock_os_error(_):
    raise OSError(2, "No such file or directory", "foo")


def mock_no_route_to_host(_):
    raise OSError(113, "No route to host", "foo")


def test_initiate_mqtt_client(mqtt_client):
    assert isinstance(mqtt_client, MQTTClient)


def test_mqtt_client_connection_to_server(mqtt_client, monkeypatch):
    mqtt_broker = MockMQTTBroker(mqtt_client.on_connect)
    monkeypatch.setattr(mqtt_client, "connect", mqtt_broker.mock_connect)
    mqtt_client.safe_connect()

    assert mqtt_client.connected_flag is True


def test_mqtt_client_connection_to_server_fail(mqtt_client, monkeypatch):
    mqtt_broker = MockMQTTBroker(mqtt_client.on_connect)
    monkeypatch.setattr(mqtt_client, "connect", mqtt_broker.mock_connect)
    monkeypatch.setattr(
        mqtt_broker,
        "reason_code",
        ReasonCodes(2, identifier=135),
    )
    with pytest.raises(TFConnectionFailed) as error:
        mqtt_client.safe_connect()

    error_value = error.value
    assert "TFConnectionFailed" in str(error_value)
    assert isinstance(error_value, TFConnectionFailed)
    assert error_value.rc == 135


def test_mqtt_client_without_options_fails():
    with pytest.raises(TypeError):
        _ = MQTTClient()


def test_mqtt_client_fail_with_no_route_to_host(mqtt_client, monkeypatch):
    monkeypatch.setattr(mqtt_client, "connect", mock_no_route_to_host)

    with pytest.raises(OSError) as error:
        mqtt_client.safe_connect(retry=1, max_retries=2)

    error_value = error.value
    assert error_value.errno == 113


def test_mqtt_client_fail_with_generic_os_error(mqtt_client, monkeypatch):
    monkeypatch.setattr(mqtt_client, "connect", mock_os_error)

    with pytest.raises(OSError) as error:
        mqtt_client.safe_connect()

    error_value = error.value
    assert error_value.errno == 2
