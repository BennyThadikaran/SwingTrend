.. Swing documentation master file, created by
   sphinx-quickstart on Tue Feb 25 17:06:20 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===================
Swing documentation
===================

The ``Swing`` class uses a mechanical approach to determine the trend of a stock along with breakout and reversal levels.

Python version: >= 3.8

No external dependencies are required.

Pandas and Mplfinance are optional requirements depending on your usage and requirements.

Introduction:
=============

The ``Swing`` class works on the same principles of **Higher Highs** and **Higher Lows** (in an uptrend) and **Lower Lows** and **Lower Highs** (in a downtrend).

.. image:: images/hh_hl.png

Within the class,

- Higher Highs and Lower Lows are called **Swing Point High (SPH)** and **Swing Point Low (SPL)**.
- Higher Lows and Lower Highs are called **Change of Character (Coc or CoCh)**.

When the price closes above the SPH, the uptrend is confirmed.

When the price closes below the SPL, the downtrend is confirmed.

 SPH forms in uptrends, while SPL forms in downtrends.

Each time the price closes above the SPH, a new CoCh price forms. Vice versa when the price closes below SPL.

  CoCh can act as an effective trailing stop to protect gains on trade positions.

In an uptrend, CoCh is the lowest point between the SPH and the candle that closes above the SPH.

In a downtrend, CoCh is the highest point between the SPL and the candle that closes below the SPL.

.. image:: images/line-structure.png

See this youtube video: `How To Understand Market Structure <https://www.youtube.com/watch?v=Pd9ASRCHWmQ&t=251>`_ for a deeper understanding.

.. toctree::

   usage
   swing_algorithm
   API_reference
