=====
Usage
=====

Installation
------------

To use ``SwingTrend``, first install it using pip:

.. code:: console

   $ pip install swingtrend

**Swing class requires atleast 40 candles (Recommended 60 candles) to get an accurate reading of the trend.**

Examples
--------

For conciseness, only the relevant bits of code have been shown.

Basic example

.. code-block:: python

  from swingtrend import Swing

  swing = Swing(retrace_threshold_pct=5)

  swing.run(sym="HDFCBANK", df=df.iloc[-60:])

  print(f"{swing.symbol} - {swing.trend}")

  if swing.trend == "UP":
      print(f"SPH: {swing.sph}, {swing.sph_dt:%d %b %Y}")
      print(f"CoCh: {swing.coc}, {swing.coc_dt:%d %b %Y}")
  elif swing.trend == "DOWN":
      print(f"SPL: {swing.spl}, {swing.spl_dt:%d %b %Y}")
      print(f"CoCh: {swing.coc}, {swing.coc_dt:%d %b %Y}")

  swing.is_sideways # bool True or False

  # Are enough candles present to accurately determine trend?
  swing.is_trend_stable # bool True or False
  
  swing.reset()

Example showing how to screen stocks

.. code-block:: python

   for sym in watchlist:
    swing.run(sym=sym.upper(), df=df.iloc[-60:])

    if swing.trend == "UP" and swing.bars_since > 4 and swing.bars_since < 15:
        # Stocks in uptrend with a pullback between 4 and 15 bars.
        print(sym)

    swing.reset() # Dont forget to reset after each iteration.

Example showing how to attach callback functions. 

Here we look for stocks which have reversed to uptrend or broken above the SPH.

The stocks are collected into a list and printed at the end.

.. code-block:: python

   breakout_lst = []
   reversal_lst = []

   # The two functions below will be attached to the Swing class
   def bos(swing: Swing, date, close, breakout_level):
      if date != swing.df.index[-1]:
          # We only want stocks for today and not previous dates.
          return

      if swing.trend == "UP" and swing.is_trend_stable:
          breakout_lst.append(swing.symbol)

          print(
              f"{date:%d %b %Y}: {swing.symbol} break @ {breakout_level} with close @ {close}"
          )

   def reversal(swing: Swing, date, close, reversal_level):
      if date != swing.df.index[-1]:
          return

      # Trend was down and now reversed to UP
      if swing.trend == "UP" and swing.is_trend_stable:
          breakout_lst.append(swing.symbol)

          print(
              f"{date:%d %b %Y}: {swing.symbol} reversed @ {reversal_level} with close @ {close}"
          )

   swing = Swing()

   # Attach the functions to Swing class
   swing.on_breakout = bos
   swing.on_reversal = reversal

   for sym in watchlist:
      swing.run(sym=sym.upper(), df=df.iloc[-60:])
      swing.reset()

  if breakout_lst:
      print("Breakouts", breakout_lst)

  if reversal_lst:
      print("Reversals", reversal_lst)

Example showing how to plot lines in mplfinance

.. code-block:: python

  import mplfinance as mpf
  from swingtrend import Swing

  swing = Swing(retrace_threshold_pct=8)

  # add `plot_lines=True`
  # here we pass additional candles since it takes 40 candles to confirm the trend.
  swing.run(sym, df.iloc[-160:], plot_lines=True)

  # `swing.plot_lines` provides the line coordinates
  # `swing.plot_colors` provides the line colors
  # Add the lines and colors to alines
  mpf.plot(
      df,
      title=f"{sym.upper()} {swing.trend}",
      type="candle",
      style="tradingview",
      scale_padding=dict(left=0.05, right=0.6, top=0.35, bottom=0.7),
      alines=dict(
          linewidths=0.8,
          alpha=0.7,
          colors=swing.plot_colors,
          alines=swing.plot_lines,
      ),
  )

Pandas is not a requirement. You can provide OHLC data from any source to ``Swing.identify``.

.. code-block:: python

  ohlc_tuple = (
    (datetime(2024, 1, 1), 100, 90, 93),
    (datetime(2024, 1, 2), 95, 85, 88),
    (datetime(2024, 1, 3), 90, 80, 83),
    (datetime(2024, 1, 4), 85, 75, 78),
  )

  swing = Swing()

  for tup in ohlc_tuple:
      swing.identify(*tup)

Debug mode is useful when trying to understand the program. Have a chart in front and read the logs.

.. code-block:: python

  import logging
  from swingtrend import Swing

  # Make sure to set basicConfig for logging
  logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)

  swing = Swing(debug=True)
