# from logging import config
# import time
# from coinbase.rest import RESTClient
# from dacite import from_dict
# from bot.sc_types import *
# from bot.sc_services import *
# from bot.config import config


# class Cancel_Service:
#     def __init__(
#         self,
#         accountService,
#         orderService,
#         orderBook,
#         api_client,
#         config: dict[CurrencyPair, CurrencyPairConfig] = config,
#     ) -> None:
#         self.accountService: AccountService = accountService
#         self.orderService: OrderService = orderService
#         self.orderBook: OrderBook = orderBook
#         self.api_client: RESTClient = api_client

#     def cancel_and_verify_orders(self, orderIds, max_retries=15):
#         if orderIds:
#             self.api_client.cancel_orders(orderIds)
#             retries = 0
#             while retries < max_retries:
#                 time.sleep(0.1)
#                 data = self.api_client.list_orders()
#                 orders = from_dict(AllOrdersList, data)
#                 if all(
#                     order.status == OrderStatus.CANCELLED.value
#                     for order in orders.orders
#                     if order.order_id in orderIds
#                 ):
#                     print("All orders have been cancelled!")
#                     break
#                 retries += 1
#             else:
#                 print(f"All orders could not be cancelled after {max_retries} retries.")

#     def cancel_orders(self, pair: CurrencyPair) -> None:
#         print(f"Cancelling orders for {pair.value}...")
#         data = self.api_client.list_orders()
#         orders = from_dict(AllOrdersList, data)
#         orderIds = [
#             order.order_id
#             for order in orders.orders
#             if order.product_id == pair.value and order.status == "OPEN"
#         ]
#         self.cancel_and_verify_orders(orderIds)

#     def cancel_all_orders(self, max_retries: int = 3) -> None:
#         print("Cancelling all orders...")
#         data = self.api_client.list_orders(order_status=["OPEN"])
#         orders = from_dict(AllOrdersList, data)
#         self.cancel_and_verify_orders(
#             [order.order_id for order in orders.orders], max_retries
#         )
