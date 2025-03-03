# SwingTrend

SwingTrend provides a mechanical approach to determine the stock trend, with breakout and reversal levels.

Python version: >= 3.8

- Can track trends on historical as well as real-time OHLC data.
- Use it as a trend indicator or screener.
- Lightweight and serializable. The Class state can be saved/restored. Useful for day-to-day tracking of trends.
- Timeframe agnostic - pass data from any timeframe to establish the current trend.
- Linux, Windows, and Mac. No external dependencies.

If you ❤️ my work so far, please 🌟 this repo.

## 👽 Documentation

[https://bennythadikaran.github.io/SwingTrend](https://bennythadikaran.github.io/SwingTrend)

## Installation

`pip install swingtrend`

## Basic Usage

```py
from swingtrend import Swing`

# Initialise with default values
swing = Swing(retrace_threshold_pct=5, sideways_threshold=20, debug=False)

swing = swing.run(sym="HDFCBANK", df.iloc[-60:])

swing.trend # UP or DOWN or None

swing.is_sideways() # True or False.

swing.sph # if trend is UP and SPH is confirmed else None

swing.spl # if trend in DOWN and SPL is confirmed else None

swing.coc # Reversal price for the current trend.

swing.high # the current highest high within a swing.

swing.low # the current lowest low within a swing.

# Below represent datetime of the respective candles.
swing.sph_dt
swing.spl_dt
swing.coc_dt
swing.high_dt
swing.low_dt
```

See the documentation for more details.

## Inspiration

This work was inspired by youtube Channel **Matt Donlevey - Photon Trading**.

You can watch their video [How To Understand Market Structure](https://www.youtube.com/watch?v=Pd9ASRCHWmQ&t=251) to understand some of the concepts.

## How the class works

See [simple explanation of how the program works](https://bennythadikaran.github.io/SwingTrend/swing_algorithm.html)

To use the Photon method as explained in the video, instantiate the class as `Swing(retrace_threshold_pct=None)`

With the Photon method, both major or minor pivots can result in trend continuation or reversal. (including a single bar pullback).

I prefer avoiding the minor pivots by setting a minimum threshold percent. With an 8% threshold, the pullback must retrace atleast 8% or more to be considered a level for trend reversal or continuation.
