API Reference
=============

.. autoclass:: swingtrend.Swing

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

Methods
-------

.. automethod:: swingtrend.Swing.run

.. automethod:: swingtrend.Swing.identify

.. automethod:: swingtrend.Swing.is_sideways

.. automethod:: swingtrend.Swing.reset

.. automethod:: swingtrend.Swing.pack

.. automethod:: swingtrend.Swing.unpack
