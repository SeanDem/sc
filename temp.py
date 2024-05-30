        # max_amount_buy_orders = self.orderBook.get_top_orders(
        #     CurrencyPair(order.product_id), OrderSide.BUY, 3, True
        # )
        # max_amount_buy_ids, max_amount_buy_amounts, max_amount_buy_prices = zip(
        #     *max_amount_buy_orders
        # )

        # self.setupService.cancel_and_verify_orders(max_amount_buy_ids)
        # total_qty = sum(max_amount_buy_amounts)
        # new_orders = list(max_amount_buy_prices) + [order.avg_price]
        # qty = total_qty / len(new_orders)
        # for price in new_orders:
        #     self.orderService.buy_order(
        #         pair=CurrencyPair(order.product_id),
        #         qty=str(qty),
        #         price=str(price),
        #     )



                # min_amount_sell_orders = self.orderBook.get_top_orders(
        #     CurrencyPair(order.product_id), OrderSide.SELL, 3, False
        # )
        # min_amount_sell_ids, min_amount_sell_amounts, min_amount_sell_prices = zip(
        #     *min_amount_sell_orders
        # )

        # self.setupService.cancel_and_verify_orders(min_amount_sell_ids)

        # total_qty = sum(min_amount_sell_amounts)
        # new_orders = list(min_amount_sell_prices) + [order.avg_price]
        # qty = total_qty / len(new_orders)
        # for price in new_orders:
        #     self.orderService.sell_order(
        #         pair=CurrencyPair(order.product_id),
        #         qty=str(qty),
        #         price=str(price),
        #     )
        
    #                 self.orderBook.delete_order_by_id(order.order_id)
    #         if order.order_side == OrderSide.BUY.value:
    #             self.handle_buy_order(order)
    #         elif order.order_side == OrderSide.SELL.value:
    #             self.handle_sell_order(order)

    # def handle_buy_order(self, order: OrderEvent) -> None:
    #     LOGGER.info(
    #         f"Buy order event filled for {order.product_id}: {order.cumulative_quantity} at {order.avg_price} USDC"
    #     )
    #     min_amount_sell_prices = self.orderBook.get_prices_with_lowest_amount(
    #         CurrencyPair(order.product_id), OrderSide.SELL
    #     )
    #     order_amount = abs(Decimal(order.cumulative_quantity)) / len(
    #         min_amount_sell_prices
    #     )
    #     for price in min_amount_sell_prices:
    #         self.orderService.sell_order(
    #             CurrencyPair(order.product_id),
    #             str(order_amount),
    #             price,
    #         )

    # def handle_sell_order(self, order: OrderEvent) -> None:
    #     LOGGER.info(
    #         f"Sell order event filled for {order.product_id}: {order.cumulative_quantity} at {order.avg_price} USDC"
    #     )
    #     max_amount_buy_prices = self.orderBook.get_prices_with_lowest_amount(
    #         CurrencyPair(order.product_id), OrderSide.BUY
    #     )
    #     order_amount = abs(Decimal(order.cumulative_quantity)) / len(
    #         max_amount_buy_prices
    #     )
    #     for price in max_amount_buy_prices:
    #         self.orderService.buy_order(
    #             CurrencyPair(order.product_id),
    #             str(order_amount),
    #             price,
    #         )