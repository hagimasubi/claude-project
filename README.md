# 株価取得プログラム（yfinance）

`yfinance` ライブラリを使って、日本株・米国株の最新株価や過去の株価データを取得・表示するシンプルなPythonプログラムです。

## 1. 必要なライブラリのインストール

ターミナル（コマンドプロンプト）で以下を実行してください。

```bash
pip install yfinance
```

または、このリポジトリの `requirements.txt` を使ってまとめてインストールすることもできます。

```bash
pip install -r requirements.txt
```

## 2. プログラムの実行方法

```bash
python stock_price.py
```

実行すると、トヨタ自動車（`7203.T`）とApple（`AAPL`）について、

- 最新の株価
- 過去1ヶ月分の株価データ（始値・高値・安値・終値・出来高）

が表示されます。

## 3. コードの解説

### 銘柄コードについて

- 日本株: 証券コードの末尾に `.T` をつけます（例: トヨタ自動車 `7203.T`）
- 米国株: そのままティッカーシンボルを使います（例: Apple `AAPL`）

### `show_latest_price(ticker_symbol)`

```python
ticker = yf.Ticker(ticker_symbol)
history = ticker.history(period="1d")
latest_price = history["Close"].iloc[-1]
```

- `yf.Ticker()` で銘柄オブジェクトを作成します。
- `.history(period="1d")` で直近1日分のデータを取得します。
- 取得したデータの `Close`（終値）列の最後の値が「最新の株価」です。

### `show_price_history(ticker_symbol, period)`

```python
history = ticker.history(period=period)
print(history[["Open", "High", "Low", "Close", "Volume"]])
```

- `period` に `"1mo"`（1ヶ月）などの期間を指定すると、その期間分の株価データ（始値・高値・安値・終値・出来高）が取得できます。
- 指定できる期間の例: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `5y`, `max`

## 4. カスタマイズ方法

`stock_price.py` の一番下にある `target_symbols` を書き換えると、調べたい銘柄を変更できます。

```python
target_symbols = ["7203.T", "AAPL"]  # ここに好きな銘柄コードを追加・変更できます
```

例えば、ソニーグループ（`6758.T`）とMicrosoft（`MSFT`）を調べたい場合は次のようにします。

```python
target_symbols = ["6758.T", "MSFT"]
```

## 5. 注意事項

- `yfinance` はYahoo! Financeのデータを利用しています。取得できるデータの正確性・リアルタイム性は保証されないため、参考情報としてご利用ください。
- インターネット接続が必要です。
- 短時間に大量のリクエストを送ると、一時的にデータが取得できなくなる場合があります。
