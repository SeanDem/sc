from sc_types import *
from sc_services import *

config: dict[CurrencyPair, CurrencyPairConfig] = {
    CurrencyPair.DAI_USDC: CurrencyPairConfig(
        CurrencyPair.DAI_USDC,
        4,
        "0.6",  # make sure this adds up to 1 or else....
        ".9997",
        ".9999",
        RangeConfig("0.9871", "0.9996", 20),
        RangeConfig(".9999", "1.0002", 2),
    ),
    CurrencyPair.PAX_USDC: CurrencyPairConfig(
        CurrencyPair.PAX_USDC,
        2,
        "0.4",  # make sure this adds up to 1 or else....
        ".9991",
        "1",
        RangeConfig("0.9814", "0.9989", 12),
        RangeConfig("1", "1.001", 2),
    ),
}
