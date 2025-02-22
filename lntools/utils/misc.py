def missing_dependency(pkg: str) -> None:
    "Raise Assertion Error for Missing Optional Dependency"
    raise AssertionError(f"Missing optional dependency: {pkg}")


def is_valid_df_lib(df_lib: str):
    if df_lib not in ['pandas', 'polars']:
        raise ValueError(f"{df_lib} is not a valid dataframe library. Please use 'pandas' or 'polars'")


def is_valid_exchange(exchange: str):
    # XSHG-上海证券交易所；XSHE-深圳证券交易所；CCFX-中金所
    if exchange not in ['XSHG', 'XSHE', 'CCFX']:
        raise ValueError(f"{exchange} is not a valid exchange. Please use 'XSHG', 'XSHE', 'CCFX'")
