## IN PROGRESS

### TODO

> [!IMPORTANT]
>
> - [ ] sqlLite in meory DB for orderbook
> - [ ] slow and steady bot. Less cancelling
> - [ ] better logging buys and sales
> - [ ] update cancel service to not need mutex

- [ ] compare total orders and orders in my orderbook info / log
- [ ] add service name to logs
- [ ] config service
- [ ] log filled orders
- [ ] cancel largest orders. Order selection cancel logic service? Newest and largest usually
- [ ] rename orderbook, order service and userOrderService, too close in name
- [ ] re-orgainize and rename files / services, number of services has grows past current design
- [ ] rebalance service - logic to keep "total orders" more stable, while keeping order book balanced. also keep oldest orders
- [ ] add more error handling
- [ ] add back other token
- [ ] add more logging
- [ ] add more tests
- [ ] cancel percent of orders not fixed amount

### DONE

- [x] convert to asyncio
- [x] smaller orders max order size config
- [x] order prices consolidating bug. think orderbook is loosing price ladder over time
- [x] docker
- [x] logic for replacing orders / replacing. -> random cancellation every 1-3 mins to keep book even
- [x] periodic check of funds not in order
- [x] Auto orderBook updating with functions. orderbook is very broken
- [x] better order cancellation logic and standalone service
- [x] add logging
- [x] each split ws thread may need heartbeat
- [x] pending tx bug
- [x] check current price before placing orders
- [x] cancel largest order to replace filled orders
- [x] bottom n or n largest cancel to refill n + 1
- [x] better service split, particularly ws_client
