## IN PROGRESS

### TODO

> [!IMPORTANT]
>
> - [ ] convert to asyncio
> - [ ] better logging buys and sales
> - [ ] slow and steady bot. Less cancelling

- [ ] compare total orders and orders in my orderbook info / log
- [ ] add service name to logs
- [ ] config service
- [ ] log filled orders
- [ ] cancel largest orders. Order selection cancel logic service? Newest and largest usually
- [ ] rename orderbook, order service and userOrderService, too close in name
- [ ] re-orgainize and rename files / services, number of services has grows past current design
- [ ] rebalance service - logic to keep "total orders" more stable, while keeping order book balanced. also keep oldest orders
- [ ] robust logic to deal with prolonged below $1 prices
- [ ] add mechanism to not cancel older orders, those benefit most from time priority
- [ ] add more error handling
- [ ] add back other token
- [ ] add more logging
- [ ] add more tests
- [ ] cancel percent of orders not fixed amount

### DONE

- [x] smaller orders max order size config
- [x] order prices consolidating bug. think orderbook is loosing price ladder over time
- [x] docker
- [x] logic for replacing orders / replacing. -> random cancellation every 1-3 mins to keep book even
- [x] periodic check of funds not in order
- [x] Auto orderBook updating with functions. orderbook is very broken
      also i do not like how it works right now. seems too complex
- [x] better order cancellation logic and standalone service
- [x] add logging
- [x] each split ws thread may need heartbeat
- [x] pending tx bug
- [x] check current price before placing orders
- [x] cancel largest order to replace filled orders
- [x] bottom n or n largest cancel to refill n + 1
- [x] better service split, particularly ws_client
