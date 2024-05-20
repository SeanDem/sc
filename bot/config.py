from sc_types import *
from sc_services import *

config: dict[CurrencyPair,CurrencyPairConfig ] = {
    CurrencyPair.DAI_USDC: CurrencyPairConfig(
        CurrencyPair.DAI_USDC,
        "0.5",
        ".9997",
        ".9999",
        RangeConfig("0.9871", "0.9995", 10),
        RangeConfig(".9999", "1.0002", 2),
    ),
    CurrencyPair.PAX_USDC: CurrencyPairConfig(
        CurrencyPair.PAX_USDC,
        "0.5",
        ".9997",
        ".9999",
        RangeConfig("0.9812", "0.9994", 10),
        RangeConfig("1", "1.0007", 2),
    ),
}
