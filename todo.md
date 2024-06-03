# TODO List

## IN PROGRESS

### TODO

- [ ] rebalance service - logic to keep "total orders" more stable, while keeping order book balanced. also keep oldest orders
- [ ] robust logic to deal with prolonged below $1 prices
- [ ] add mechanism to not cancel older orders, especially those at at a lower price. those benefit most from time priority
- [ ] check on threading, we probably need more thread locking
- [ ] Add more error handling
- [ ] add back other token
- [ ] Add more logging
- [ ] Add more tests

### DONE

- [x] Smaller orders max order size config?
- [x] order prices consolidating bug. think orderbook is loosing price ladder over time
- [x] Docker
- [x] logic for replacing orders / replacing. -> random cancellation every 1-3 mins to keep book even
- [x] periodic check of funds not in order
- [x] Auto orderBook updating with functions. orderbook is very broken
      also i do not like how it works right now. seems too complex
- [x] Better order cancellation logic and standalone service
- [x] Add logging
- [x] Each split ws thread may need heartbeat
- [x] Pending tx bug
- [x] Check current price before placing orders
- [x] Cancel largest order to replace filled orders
- [x] Bottom n or n largest cancel to refill n + 1
- [x] Better service split, particularly ws_client
