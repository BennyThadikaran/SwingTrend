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

  swing.is_sideways() # bool True or False
  
  swing.reset()

Example showing how to plot lines in mplfinance

.. code-block:: python

  import mplfinance as mpf
  from swingtrend import Swing

  swing = Swing(retrace_threshold_pct=8)

  # add `plot_lines=True`
  # here we pass additional candles since it takes 40 candles to confirm the trend.
  swing.run(sym, df.iloc[-160:], plot_lines=True)

  # Once swing.run completes,
  # swing.plot_lines provides the line coordinates
  # swing.plot_colors provides the line colors

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
