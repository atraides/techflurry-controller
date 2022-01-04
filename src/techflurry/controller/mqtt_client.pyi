from typing import Any, Dict, List, Optional, Type, Union

from paho.mqtt.client import Client, MQTTMessage as MQTTMessage

MQTT_CLIENT_KWARGS = Optional[Union[str, Union[int, bool]]]

class MQTTClient(Client):
    last_pub_time: int
    run_flag: bool
    subscribe_flag: bool
    bad_connection_flag: bool
    connected_flag: bool
    disconnect_flag: bool
    disconnect_time: float
    pub_msg_count: int
    mqtt_topic: str
    def __init__(
        self,
        topic: Optional[str] = None,
        protocol: int = ...,
        **kwargs: Dict[str, MQTT_CLIENT_KWARGS]
    ) -> None: ...
    def connect_function(
        self,
        client: object,  # @TODO: Proper typehint for objects like Type[T]
        userdata: Optional[str],
        flags: Dict[str, Any],
        rc: str,
        *args: List[Any]
    ) -> None: ...
    def message_function(
        self, client: object, userdata: Optional[str], msg: MQTTMessage
    ) -> None: ...
    def safe_connect(self, hostname: str, retry: int = ...) -> None: ...
