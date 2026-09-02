"""
株価取得プログラム（土台）

yfinance を使って、キーボードで入力した銘柄コードの最新の株価情報を
初心者にも分かりやすい日本語のテキストで表示します。

使い方:
    python stock_price.py
    実行後、画面の指示に従って銘柄コードを入力してください。

銘柄コードの例:
    - トヨタ自動車（東証）: 7203.T   ※日本株は末尾に ".T" をつける
    - Apple（米国株）    : AAPL
"""

import yfinance as yf

# 銘柄コード -> 日本語の会社名（登録がない銘柄は yfinance から取得した英語名を使う）
COMPANY_NAMES = {
    "7203.T": "トヨタ自動車",
    "6758.T": "ソニーグループ",
    "9984.T": "ソフトバンクグループ",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet（Google）",
    "TSLA": "テスラ",
}

# 通貨コード -> 表示する単位
CURRENCY_UNITS = {
    "JPY": "円",
    "USD": "ドル",
}


def get_company_name(ticker: yf.Ticker, ticker_symbol: str) -> str:
    """会社名を取得する（登録済みの日本語名がなければ yfinance の情報を使う）"""
    if ticker_symbol in COMPANY_NAMES:
        return COMPANY_NAMES[ticker_symbol]

    try:
        info = ticker.info
        return info.get("longName") or info.get("shortName") or ticker_symbol
    except Exception:
        return ticker_symbol


def get_currency_unit(ticker: yf.Ticker) -> str:
    """通貨コードから表示用の単位（円・ドルなど）を取得する"""
    currency_code = None
    try:
        currency_code = ticker.fast_info.currency
    except Exception:
        pass

    if not currency_code:
        try:
            currency_code = ticker.info.get("currency")
        except Exception:
            currency_code = None

    return CURRENCY_UNITS.get(currency_code, currency_code or "")


def format_amount(value: float, unit: str) -> str:
    """金額を単位付きの文字列に整形する（円は整数、それ以外は小数点2桁）"""
    if unit == "円":
        return f"{value:,.0f}{unit}"
    return f"{value:,.2f}{unit}"


def format_diff(value: float, unit: str) -> str:
    """前日比の金額を符号付き（+/-）の文字列に整形する"""
    if unit == "円":
        return f"{value:+,.0f}{unit}"
    return f"{value:+,.2f}{unit}"


def show_stock_summary(ticker_symbol: str) -> None:
    """指定した銘柄コードの最新1日分の株価を、日本語で分かりやすく表示する"""
    ticker = yf.Ticker(ticker_symbol)

    # 前日比を計算するため直近5日分を取得し、末尾2日分を使う
    history = ticker.history(period="5d")

    if history.empty:
        print(f"【銘柄】{ticker_symbol}")
        print("株価データが取得できませんでした。銘柄コードを確認してください。")
        print("-" * 40)
        return

    latest = history.iloc[-1]
    latest_date = history.index[-1]
    previous_close = history.iloc[-2]["Close"] if len(history) >= 2 else None

    name = get_company_name(ticker, ticker_symbol)
    unit = get_currency_unit(ticker)

    open_price = latest["Open"]
    high_price = latest["High"]
    low_price = latest["Low"]
    close_price = latest["Close"]

    print("---------")
    print(f"【銘柄】{name} ({ticker_symbol})")
    print(f"【日付】{latest_date.year}年{latest_date.month}月{latest_date.day}日")
    print(f"【始値】{format_amount(open_price, unit)}")
    print(f"【高値】{format_amount(high_price, unit)}")
    print(f"【安値】{format_amount(low_price, unit)}")
    print(f"【終値（現在の株価）】{format_amount(close_price, unit)}")

    if previous_close is not None and previous_close != 0:
        diff = close_price - previous_close
        percent = diff / previous_close * 100
        print(f"【前日比】{format_diff(diff, unit)} ({percent:+.1f}%)")
    else:
        print("【前日比】データなし")
    print("---------")


def show_intro() -> None:
    """起動時に表示する説明とヒント"""
    print("=" * 40)
    print("株価チェックプログラム")
    print("=" * 40)
    print("調べたい銘柄のコードを入力してください。")
    print()
    print("【入力例】")
    print("  日本株：トヨタ自動車 → 7203.T　／　ソニーグループ → 6758.T")
    print("  米国株：Apple → AAPL　／　テスラ → TSLA")
    print("  ※日本株は証券コードの後ろに「.T」を付けてください")
    print("  ※何も入力せず Enter を押すと終了します")
    print("-" * 40)


if __name__ == "__main__":
    show_intro()

    try:
        while True:
            ticker_symbol = input("調べたい銘柄のコードを入力してください： ").strip()

            if not ticker_symbol:
                print("プログラムを終了します。")
                break

            try:
                show_stock_summary(ticker_symbol.upper())
            except Exception as error:
                print(f"エラーが発生しました：{error}")
                print("銘柄コードが正しいか確認して、もう一度お試しください。")
            print()
    except (KeyboardInterrupt, EOFError):
        print("\nプログラムを終了します。")
