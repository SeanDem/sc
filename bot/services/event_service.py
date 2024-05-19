from coinbase.websocket import WSClient


class EventService(WSClient):

    def __init__(
        self, api_key: str, api_secret: str, on_open, on_message, on_close
    ) -> None:
        super().__init__(api_key, api_secret, on_open, on_message, on_close)
