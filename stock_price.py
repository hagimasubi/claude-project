"""
株価取得プログラム

企業名（日本語・英語どちらでもOK）を入力するだけで、
Yahoo Finance の検索機能を使って自動的に銘柄コード（ティッカー）を見つけ出し、
最新の株価を分かりやすい日本語のテキストで表示します。

使い方:
    python stock_price.py
    実行後、画面の指示に従って調べたい企業名を入力してください。

入力例:
    トヨタ / ソニー / アップル / Toyota / Apple / Tesla など
    （7203.T や AAPL のように銘柄コードを直接入力してもOKです）
"""

from typing import Optional

import requests
import yfinance as yf

# Yahoo Finance の銘柄検索API
SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"
REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# 銘柄コード -> 日本語の会社名（登録がない銘柄は検索結果や yfinance の英語名を使う）
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


def search_ticker(keyword: str) -> Optional[dict]:
    """企業名（または銘柄コード）から、該当する銘柄情報を検索する

    Yahoo Finance の検索API（SEARCH_URL）に問い合わせて、
    最も一致度の高い株式（EQUITY）を1件返す。見つからなければ None。
    """
    params = {"q": keyword, "quotesCount": 5, "newsCount": 0}
    response = requests.get(
        SEARCH_URL, params=params, headers=REQUEST_HEADERS, timeout=10
    )
    response.raise_for_status()
    quotes = response.json().get("quotes", [])

    # 株式（EQUITY）を優先的に選ぶ。なければ最初の候補を使う
    equities = [q for q in quotes if q.get("quoteType") == "EQUITY"]
    candidates = equities or quotes

    return candidates[0] if candidates else None


def get_company_name(ticker: yf.Ticker, ticker_symbol: str, search_name: Optional[str]) -> str:
    """会社名を取得する（日本語名の登録 > 検索結果の名前 > yfinance の英語名 の順）"""
    if ticker_symbol in COMPANY_NAMES:
        return COMPANY_NAMES[ticker_symbol]

    if search_name:
        return search_name

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


def show_stock_summary(ticker_symbol: str, search_name: Optional[str] = None) -> None:
    """指定した銘柄コードの最新1日分の株価を、日本語で分かりやすく表示する"""
    ticker = yf.Ticker(ticker_symbol)

    # 前日比を計算するため直近5日分を取得し、末尾2日分を使う
    history = ticker.history(period="5d")

    if history.empty:
        print(f"【銘柄】{ticker_symbol}")
        print("株価データが取得できませんでした。銘柄コードを確認してください。")
        return

    latest = history.iloc[-1]
    latest_date = history.index[-1]
    previous_close = history.iloc[-2]["Close"] if len(history) >= 2 else None

    name = get_company_name(ticker, ticker_symbol, search_name)
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


def lookup_and_show(keyword: str) -> None:
    """企業名（または銘柄コード）を検索し、見つかった銘柄の株価レポートを表示する"""
    try:
        match = search_ticker(keyword)
    except requests.exceptions.RequestException as error:
        print(f"銘柄の検索中にエラーが発生しました：{error}")
        print("インターネット接続を確認して、もう一度お試しください。")
        return

    if not match:
        print(f"「{keyword}」に一致する銘柄が見つかりませんでした。別のキーワードでお試しください。")
        return

    ticker_symbol = match.get("symbol")
    search_name = match.get("longname") or match.get("shortname")

    print(f"→「{keyword}」から銘柄コード「{ticker_symbol}」を見つけました。")

    try:
        show_stock_summary(ticker_symbol, search_name=search_name)
    except Exception as error:
        print(f"株価データの取得中にエラーが発生しました：{error}")


def show_intro() -> None:
    """起動時に表示する説明とヒント"""
    print("=" * 40)
    print("株価チェックプログラム")
    print("=" * 40)
    print("調べたい企業名を入力してください。")
    print()
    print("【入力例】")
    print("  日本語：トヨタ　／　ソニー　／　ソフトバンク")
    print("  英語　：Apple　／　Tesla　／　Microsoft")
    print("  ※7203.T や AAPL のように銘柄コードを直接入力してもOKです")
    print("  ※何も入力せず Enter を押すと終了します")
    print("-" * 40)


if __name__ == "__main__":
    show_intro()

    try:
        while True:
            keyword = input("調べたい企業名を入力してください： ").strip()

            if not keyword:
                print("プログラムを終了します。")
                break

            lookup_and_show(keyword)
            print()
    except (KeyboardInterrupt, EOFError):
        print("\nプログラムを終了します。")
