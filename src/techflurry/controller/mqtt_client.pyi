from typing import Any, Dict, List, Optional, Type, Union

from paho.mqtt.client import Client  # type: ignore[import]
from paho.mqtt.client import MQTTMessage as MQTTMessage

MQTT_CLIENT_KWARGS = Optional[Union[str, Union[int, bool]]]

class MQTTClient(Client):  # type: ignore[no-any-unimported]
    last_pub_time: int
    run_flag: bool
    subscribe_flag: bool
    bad_connection_flag: bool
    connected_flag: bool
    disconnect_flag: bool
    disconnect_time: float
    pub_msg_count: int
    hostname: str
    mqtt_topic: str
    def __init__(
        self,
        hostname: str,
        topic: str,
        protocol: int = ...,
        **kwargs: Dict[str, MQTT_CLIENT_KWARGS]
    ) -> None: ...
    def on_connect(
        self,
        client: object,  # @TODO: Proper typehint for objects like Type[T]
        userdata: Optional[str],
        flags: Dict[str, Any],
        rc: str,
        *args: List[Any]
    ) -> None: ...
    def on_message(  # type: ignore[no-any-unimported]
        self, client: object, userdata: Optional[str], msg: Type[MQTTMessage]
    ) -> None: ...
    def shutdown(self) -> None: ...
    def safe_connect(self, retry: int = ...) -> None: ...
