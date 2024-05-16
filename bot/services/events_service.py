from coinbase.websocket import WSClient


class EventService(WSClient):
    def __init__(
        self,
        api_key: str,
        api_secret: str,
    ) -> None:
        super().__init__(
            api_key=api_key,
            api_secret=api_secret,
            on_close=self.on_close,
            on_open=self.on_open,
            on_message=self.on_message,
        )

    def on_open(self) -> None:
        self.message_count = 0
        print("WebSocket is now open!")

    def on_message(self, msg) -> None:
        self.message_count += 1
        if (
            msg["type"] == "match" and msg["side"] == "buy"
        ):  # Filter messages for buy events
            print("Buy Event:", msg)

    def on_close(self) -> None:
        print("WebSocket is now closed!")
