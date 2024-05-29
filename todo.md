# TODO List

## IN PROGRESS

- [ ] Auto orderBook updating with functions. orderbook is very broken
      also i do not like how it works right now. seems too complex

### TODO

- [ ] Double orders on setup
- [ ] Check on threading
- [ ] Add more error handling
- [ ] Add more tests

### DONE

- [x] Better order cancellation logic and standalone service
- [x] Add logging
- [x] Each split ws thread may need heartbeat
- [x] Pending tx bug
- [x] Check current price before placing orders
- [x] Cancel largest order to replace filled orders
  - [x] Bottom n or n largest cancel to refill n + 1
- [x] Better service split, particularly ws_client
