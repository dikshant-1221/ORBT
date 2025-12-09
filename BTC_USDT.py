from google.colab import files
import io
upload = files.upload()
import pandas as pd
import plotly.graph_objects as go


# Load dataset
data = pd.read_feather("BTC_USDT_USDT-15m-futures.feather")
data.head(12)


# Date ko datetime me convert

data["date"] = pd.to_datetime(data["date"])

# Date index
data = data.set_index("date")


# only for selected dates aur time

data = data.loc["2023-11-01":"2023-11-12"]
data = data.between_time("00:00", "23:59")

# New columns signals aur ORB lines

data["signal"] = ""
data["ORH"] = None    # ORB High
data["ORL"] = None    # ORB Low


# every day new ORB

for day_name, day_rows in data.groupby(data.index.date):


    one_day = data.loc[str(day_name)]

    # 8:00 se 8:15 wali candle -> ORB candle
    orb_candle = one_day.between_time("08:00", "08:15")

    # Agar ORB candle nahi mili toh aage jao
    if len(orb_candle) == 0:
        continue

    # ORB high-low
    ORB_high = orb_candle.iloc[0]["high"]
    ORB_low  = orb_candle.iloc[0]["low"]

    #  ORH/ORL
    data.loc[str(day_name), "ORH"] = ORB_high
    data.loc[str(day_name), "ORL"] = ORB_low

    # New day = no previous signal
    last_signal = None


    # Har candle par signal check karo

    for i in range(len(one_day)):

        candle = one_day.iloc[i]

        open_price  = candle["open"]
        close_price = candle["close"]

        # OPEN price ORB ke andar hona chahiye
        if ORB_low < open_price < ORB_high:

            # BUY breakout: close ORB high ke upar
            if close_price > ORB_high and last_signal != "BUY":
                data.loc[candle.name, "signal"] = "BUY"
                last_signal = "BUY"

            # SELL breakout: close ORB low ke niche
            elif close_price < ORB_low and last_signal != "SELL":
                data.loc[candle.name, "signal"] = "SELL"
                last_signal = "SELL"

            else:
                data.loc[candle.name, "signal"] = "HOLD"

        else:
            data.loc[candle.name, "signal"] = "HOLD"




# Chart banana

fig = go.Figure()

# Candlestick chart
fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["open"],
    high=data["high"],
    low=data["low"],
    close=data["close"],
    name="Candles"
))

# ORH line (top line)
fig.add_trace(go.Scatter(
    x=data.index,
    y=data["ORH"],
    mode="lines",
    name="ORH",
    line=dict(color="green", dash="dot")
))

# ORL line (bottom line)
fig.add_trace(go.Scatter(
    x=data.index,
    y=data["ORL"],
    mode="lines",
    name="ORL",
    line=dict(color="red", dash="dot")
))

# BUY markers
buy_points = data[data["signal"] == "BUY"]
fig.add_trace(go.Scatter(
    x=buy_points.index,
    y=buy_points["close"],
    mode="markers",
    marker=dict(size=12, color="blue", symbol="triangle-up"),
    name="BUY"
))

# SELL markers
sell_points = data[data["signal"] == "SELL"]
fig.add_trace(go.Scatter(
    x=sell_points.index,
    y=sell_points["close"],
    mode="markers",
    marker=dict(size=12, color="white", symbol="triangle-down"),
    name="SELL"
))

fig.update_layout(
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    height=850
)

fig.show()
