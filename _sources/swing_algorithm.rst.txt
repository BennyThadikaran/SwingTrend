===============
Swing Algorithm
===============

.. image:: swing-illustration-1.png

Refering to the image and the counts marked therein, 

1. This is the first bar. The current trend is None. We mark the high and low of the bar. 

2. Bar breaks to the downside. The trend is now set to DOWN. The second bar marks a new low. 

3. Bar 3 continues to make new lows.

4. At 4, the bar failed to make a new low. Bar 3 low (Yellow line) is marked as a Swing Point Low (SPL). We keep track of the high being made. The next bar makes a new high point at 157.75 (line marked Red) which is the highest point reached.

5. Bar marked 5 closes below the SPL. This results in Break Of Structure (BOS). A BOS confirms the current downtrend. At this point, the high point of 157.75 is marked as Change of Character (CoCH) level.

  CoCh marks the reversal level. If this level is broken, it results in reversal of trend.

6. At 6, we see another new SPL level, followed by a Break of Structure (BOS), which create a new CoCh level at 151.8.

7. At 7, the CoCh level of 151.8 is broken with a close above. The trend has now reversed and marked as UP. The lowest point of 130.25 is marked as new CoCh level.

In Summary:
===========

**In an uptrend,**

* When a bar fails to make new high, the most recent high is marked a Swing Point High (SPH).
* CoCh is the lowest retracement point between the SPH high and the BOS (breakout bar).
* CoCh is only confirmed when the bar closes above the SPH high.

**In a downtrend,**

* When a bar fails to make new low, the most recent low is marked a Swing Point Low (SPL).
* CoCh is the highest retracement point between the SPL low and the BOS (breakdown bar).
* CoCh is only confirmed when the bar closes below the SPL.

Another explanation
===================

.. image:: swing-no-retrace-pct.png

Upon initialization, the trend is None.

On the first candle, the high and low are marked as swing high and swing low.

On subsequent candles, if either side breaks, the trend direction is set:

* If the low is broken, the trend is DOWN, and the high is marked as COC (Change of Character).
* If the high is broken, the trend is UP, and the low is marked as COC.

Once the trend is set, every new high or low in the direction of the trend is marked as a
**swing high** or **swing low** (in the Swing class, self.high and self.low).

If a candle fails to make a new high or new low in the direction of the trend,
the unbroken high or low is marked as a **SPH (Swing Point High)** or
**SPL (Swing Point Low)**.

When an SPH or SPL level is broken by a candle close, it is called a **Break of Structure (BOS)**.

  A Break of Structure (BOS) confirms the existing trend direction.

* When an SPH is broken, the lowest retracement point is marked as CoCh.
* When an SPL is broken, the highest retracement point is marked as CoCh.

    If COC is broken by a candle close, it confirms a reversal in trend.

Retrace Threshold percent
=========================

.. image:: retrace_pct-illustration.png

The ``retrace_threshold_pct`` parameter is used to decide when a BOS is confirmed.

If ``retrace_threshold_pct`` is set to a percentage:

* A BOS is only confirmed if the price retraced below the threshold.

* Example: If ``retrace_threshold_pct`` is set to 5 percent, the price must retrace below 5%
  before the SPH is broken. If not, the BOS is ignored.

If ``retrace_threshold_pct`` is ``None``, anytime an SPH is broken, it is treated as a BOS
regardless of retracement.
