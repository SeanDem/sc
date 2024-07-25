from bot.sc_types import *
from bot.sc_services import *

order_size = 25

sc_config: dict[CurrencyPair, CurrencyPairConfig] = {
    CurrencyPair.DAI_USDC: CurrencyPairConfig(
        CurrencyPair.DAI_USDC,
        4,
        "1",
        ".99985",
        ".99985",
        RangeConfig("0.988", "0.9995", 50, Skew(SkewDirection.END, 2.8)),
        RangeConfig(".9999", ".9999", 1),
    ),
    # CurrencyPair.PAX_USDC: CurrencyPairConfig(
    #     CurrencyPair.PAX_USDC,
    #     2,
    #     "0",
    #     ".9991",
    #     "1",
    #     RangeConfig("0.9814", "0.9985", 25),
    #     RangeConfig("1", "1.0018", 4),
    # ),
}
