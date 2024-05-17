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
            verbose=True,
        )

    def on_open(self) -> None:
        self.message_count = 0
        print("WebSocket is now open!")

    def on_message(self, msg) -> None:
        self.message_count += 1
        print("Buy Event:", msg)
        print(f"Message count: {self.message_count}")

    def on_close(self) -> None:
        print("WebSocket is now closed!")
