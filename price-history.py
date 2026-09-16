import json
import os
from datetime import datetime, timezone, timedelta


STOCKS_FILE = "stocks.json"
HISTORY_FILE = "price-history.json"

# 最多保留 90 個交易日
MAX_DAYS = 90


def load_json(filename, default):
    if not os.path.exists(filename):
        return default

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: 無法讀取 {filename}: {e}")
        return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


# -----------------------------
# 讀取今天的股票資料
# -----------------------------

stocks_data = load_json(
    STOCKS_FILE,
    {}
)

stocks = stocks_data.get(
    "stocks",
    []
)

if not stocks:
    raise RuntimeError(
        "stocks.json 沒有股票資料"
    )


# -----------------------------
# 讀取既有歷史資料
# -----------------------------

history_data = load_json(
    HISTORY_FILE,
    {
        "version": "1.0",
        "stocks": {}
    }
)

if not isinstance(
    history_data.get("stocks"),
    dict
):
    history_data["stocks"] = {}


# -----------------------------
# 使用台北日期
# -----------------------------

taipei_tz = timezone(
    timedelta(hours=8)
)

today = datetime.now(
    taipei_tz
).strftime("%Y-%m-%d")


# -----------------------------
# 加入今天收盤價
# -----------------------------

updated_count = 0

for stock in stocks:

    code = str(
        stock.get("code", "")
    ).strip()

    name = str(
        stock.get("name", "")
    ).strip()

    price = stock.get("price")

    if not code:
        continue

    try:
        close = float(price)
    except (TypeError, ValueError):
        continue

    if close <= 0:
        continue

    item = history_data[
        "stocks"
    ].get(
        code,
        {
            "name": name,
            "history": []
        }
    )

    item["name"] = name

    history = item.get(
        "history",
        []
    )

    if not isinstance(history, list):
        history = []

    # 清除格式錯誤的舊資料
    history = [
        x for x in history
        if isinstance(x, dict)
        and x.get("date")
        and x.get("close") is not None
    ]

    # 同一天重跑時，
    # 先刪掉舊的同日資料
    history = [
        x for x in history
        if x.get("date") != today
    ]

    history.append(
        {
            "date": today,
            "close": close
        }
    )

    # 日期排序
    history.sort(
        key=lambda x:
        x.get("date", "")
    )

    # 只保留最近 90 個交易日
    history = history[
        -MAX_DAYS:
    ]

    item["history"] = history

    history_data[
        "stocks"
    ][code] = item

    updated_count += 1


# -----------------------------
# 更新檔案資訊
# -----------------------------

history_data[
    "version"
] = "1.0"

history_data[
    "updated"
] = datetime.now(
    taipei_tz
).isoformat()

history_data[
    "market"
] = "TWSE"

history_data[
    "stock_count"
] = len(
    history_data["stocks"]
)


# -----------------------------
# 儲存
# -----------------------------

save_json(
    HISTORY_FILE,
    history_data
)


print()
print(
    "=========================="
)

print(
    "Price history updated"
)

print(
    "Date:",
    today
)

print(
    "Stocks updated:",
    updated_count
)

print(
    "Stocks in history:",
    len(history_data["stocks"])
)

print(
    "=========================="
)
