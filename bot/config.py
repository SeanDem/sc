from sc_types import *
from sc_services import *

config: dict[CurrencyPair, CurrencyPairConfig] = {
    CurrencyPair.DAI_USDC: CurrencyPairConfig(
        CurrencyPair.DAI_USDC,
        4,
        "0.7",
        ".9997",
        ".9999",
        RangeConfig("0.9865", "0.9997", 30),
        RangeConfig(".9999", "1.0004", 2),
    ),
    CurrencyPair.PAX_USDC: CurrencyPairConfig(
        CurrencyPair.PAX_USDC,
        2,
        "0.3",
        ".9991",
        "1",
        RangeConfig("0.9814", "0.9991", 15),
        RangeConfig("1", "1.0018", 2),
    ),
}
