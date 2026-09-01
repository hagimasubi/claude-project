"""
株価取得プログラム（土台）

yfinance を使って、指定した銘柄コードの
「最新の株価」と「過去の株価データ」を取得して表示します。

使い方:
    python stock_price.py

銘柄コードの例:
    - トヨタ自動車（東証）: 7203.T   ※日本株は末尾に ".T" をつける
    - Apple（米国株）    : AAPL
"""

import yfinance as yf


def show_latest_price(ticker_symbol: str) -> None:
    """指定した銘柄コードの最新の株価を表示する"""
    ticker = yf.Ticker(ticker_symbol)

    # 直近1日分のデータから最新の終値を取得
    history = ticker.history(period="1d")

    if history.empty:
        print(f"[{ticker_symbol}] データが取得できませんでした。銘柄コードを確認してください。")
        return

    latest_price = history["Close"].iloc[-1]
    print(f"[{ticker_symbol}] 最新の株価: {latest_price:.2f}")


def show_price_history(ticker_symbol: str, period: str = "1mo") -> None:
    """指定した銘柄コードの過去の株価データを表示する

    period の指定例: 1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, max
    """
    ticker = yf.Ticker(ticker_symbol)
    history = ticker.history(period=period)

    if history.empty:
        print(f"[{ticker_symbol}] 過去データが取得できませんでした。")
        return

    print(f"\n[{ticker_symbol}] 過去の株価データ（期間: {period}）")
    print(history[["Open", "High", "Low", "Close", "Volume"]])


if __name__ == "__main__":
    # 調べたい銘柄コードをここに入れてください
    target_symbols = ["7203.T", "AAPL"]  # トヨタ自動車, Apple

    for symbol in target_symbols:
        show_latest_price(symbol)
        show_price_history(symbol, period="1mo")
        print("-" * 40)
