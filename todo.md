# TODO List

## IN PROGRESS

### TODO

- [ ] Better order cancellation logic and standalone service
- [ ] Auto orderBook updating with functions. it's out of sync
- [ ] Double orders on setup
- [ ] Check on threading
- [ ] Add logging
- [ ] Add more error handling
- [ ] Add more tests

### DONE

- [x] Each split ws thread may need heartbeat
- [x] Pending tx bug
- [x] Check current price before placing orders
- [x] Cancel largest order to replace filled orders
  - [x] Bottom n or n largest cancel to refill n + 1
- [x] Better service split, particularly ws_client
