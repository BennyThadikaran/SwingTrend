=============
API Reference
=============

.. automodule:: swingtrend
   :members: Swing
   :member-order: groupwise

Swing Class Properties
======================

.. attribute:: on_reversal: Callable or None

   A optional function or class method that is called when a trend reversal occurs.


   **Swing.on_reversal** has the below signature:

   ``def on_reversal(cls: Swing, date, close: float, reversal_level: float)``

   Parameters:

   cls - The Swing class instance which provides access to all its properties and methods.

   date - The bar date on which the reversal occured.

   close - The closing price of the reversal bar.

   reversal_level - The coc price level that was broken.


.. attribute:: on_breakout: Callable or None

   A optional function or class method that is called when a Break of Structure (BOS) or breakout/breakdown occurs.

   **Swing.on_breakout** has the below signature.

   ``def on_breakout(cls: Swing, date, close: float, breakout_level: float)``

   Parameters:

   cls - The Swing class instance which provides access to all its properties and methods.

   date - The bar date on which the breakout occured.

   close - The closing price of the breakout bar.

   breakout_level - The breakout price or SPH/SPL level that was broken.

.. attribute:: symbol: str or None

   The current symbol name if passed during ``Swing.run``.

.. attribute:: df: pandas.DataFrame or None

   pandas.DataFrame if passed during ``Swing.run``.

.. attribute:: trend: str or None

  The current trend as ``UP`` or ``DOWN``. Set to None, if too few candles were supplied.

.. attribute:: sph: float or None

  The current swing point high. Set to None, if trend is Down or sph not yet formed.

.. attribute:: spl: float or None

  The current swing point low. Set to None, if trend is UP or spl not yet formed.

.. attribute:: coc: float or None

  Change of Character. It represents the trend reversal level. If trend is None, coc is None.

.. attribute:: high: float or None

  The highest price reached within the current structure. Reset to None, when SPL is formed or a trend reversal has occured.

.. attribute:: low: float or None

  The lowest price reached within the current structure. Reset to None, when SPH is formed or a trend reversal has occured.

Note regarding dates
--------------------

**Swing class does not perform any datetime operations**.

All properties below are based on the input type. If you passed a str or timestamp or datetime, the same type is returned for the properties.

.. attribute:: sph_dt: datetime or None

  Date of SPH candle formation.

.. attribute:: spl_dt: datetime or None

  Date of SPL candle formation.

.. attribute:: coc_dt: datetime or None

  Date of coc candle.

.. attribute:: low_dt: datetime or None

  Candle date with lowest price in the current structure.

.. attribute:: high_dt: datetime or None

  Candle date with highest price in the current structure.
