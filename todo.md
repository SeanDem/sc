# TODO List

## IN PROGRESS

- [ ] rebalance service

### TODO

- [ ] periodic check of funds not in order
- [ ] Check on threading
- [ ] logic for replacing orders / replacing. Cancel? Time? never?
- [ ] Add more error handling
- [ ] Smaller orders. max order size fn?
- [ ] Add more tests

### DONE

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
