import unittest
from datetime import datetime
from unittest.mock import Mock

from context import Swing


class TestSwing(unittest.TestCase):
    """
    Following test cases are covered
    pack and reset function

    When trend is None

    - First bar sets high and low
    - New high but close below high
    - New low but close above low
    - Close above high
    - Close below low

    When trend is UP

    - No SPH and new high
    - No SPH and bar fails to make new High
    - Reversal to downtrend
    - callbacks is attached and called on reveral and breakout
    - SPH is set and new high but fails to break SPH
    - trend continuation
    - SPH broken but retracement below threshold
    - SPH broken and retracement above threshold

    When trend is DOWN

    - No SPL and new low
    - No SPL and bar fails to make new Low
    - Reversal to uptrend
    - callback is attached and called on reversal and breakout
    - SPL is set and new low but fails to break SPL
    - trend continuation
    - SPL broken but retracement below threshold
    - SPL broken but retracement above threshold
    """

    def setUp(self) -> None:
        self.swing = Swing(retrace_threshold_pct=None)

    def test_pack(self):
        """Test there are no callables or unserializable objects after packing"""

        self.swing.on_breakout = self.swing.on_reversal = print
        self.swing.df = ""

        dct = self.swing.pack()
        self.assertIsInstance(dct, dict)

        # No callables or unserializable objects in dict
        self.assertNotIn("on_reversal", dct)
        self.assertNotIn("on_breakout", dct)
        self.assertNotIn("logger", dct)
        self.assertNotIn("df", dct)

    def test_is_sideways(self):
        self.assertEqual(self.swing.is_sideways, False)

        self.swing.unpack(dict(_Swing__bars_since=25, sideways_threshold=20))

        self.assertEqual(self.swing.is_sideways, True)

    def test_is_trend_stable(self):
        self.assertEqual(self.swing.is_trend_stable, False)

        self.swing.unpack(
            dict(_Swing__total_bar_count=60, minimum_bar_count=40)
        )

        self.assertEqual(self.swing.is_trend_stable, True)

        self.swing.unpack(
            dict(_Swing__total_bar_count=35, minimum_bar_count=40)
        )

        self.assertEqual(self.swing.is_trend_stable, False)

    def test_reset(self):
        data = dict(
            high=100,
            low=90,
            trend="UP",
            coc=85,
            sph=100,
            spl=90,
            high_dt="",
            low_dt="",
            coc_dt="",
            sph_dt="",
            spl_dt="",
            _Swing__bars_since=9,
            df="",
        )

        self.swing.unpack(data)
        self.swing.reset()

        self.assertEqual(self.swing.bars_since, 0)
        self.assertEqual(self.swing.leg_count, 0)

        data.pop("_Swing__bars_since")

        for key in data.keys():
            self.assertIsNone(getattr(self.swing, key))

        self.assertEqual(self.swing.bars_since, 0)

    def test_retrace_threshold_setter(self):
        self.assertIsNone(self.swing.retrace_threshold_pct)

        self.swing.retrace_threshold_pct = 5

        self.assertEqual(self.swing.retrace_threshold_pct, 5)

        sw = Swing(retrace_threshold_pct=10)
        self.assertEqual(sw.retrace_threshold_pct, 10)

    def test_first_bar(self):
        """First bar marks the high and low"""

        dt = datetime(2024, 1, 1)
        self.swing.identify(dt, 110, 90, 100)

        self.assertEqual(self.swing.high, 110)
        self.assertEqual(self.swing.low, 90)
        self.assertIsNone(self.swing.trend)

        self.assertEqual(self.swing.high_dt, dt)
        self.assertEqual(self.swing.low_dt, dt)

    def test_second_bar_new_high_close_below_first_high(self):
        """Second bar makes new high, fails to close above"""

        dt = datetime(2024, 1, 1)
        self.swing.unpack(dict(high=110, low=90))
        self.swing.identify(dt, 112, 95, 102)

        self.assertEqual(self.swing.high, 112)
        self.assertEqual(self.swing.low, 90)
        self.assertIsNone(self.swing.trend)

    def test_second_bar_new_low_close_above_first_low(self):
        """Second bar makes new low, fails to close below"""

        dt = datetime(2024, 1, 1)
        self.swing.unpack(dict(high=110, low=90))
        self.swing.identify(dt, 108, 85, 91)

        self.assertEqual(self.swing.high, 110)
        self.assertEqual(self.swing.low, 85)
        self.assertIsNone(self.swing.trend)

    def test_second_bar_close_below_first_low(self):
        dt_1 = datetime(2024, 1, 1)
        dt_2 = datetime(2024, 1, 2)

        self.swing.unpack(dict(high=100, low=90, high_dt=dt_1, low_dt=dt_1))
        self.swing.identify(dt_2, 95, 85, 85)

        self.assertEqual(self.swing.high, 100)
        self.assertEqual(self.swing.low, 85)
        self.assertEqual(self.swing.trend, "DOWN")

        self.assertEqual(self.swing.high_dt, dt_1)
        self.assertEqual(self.swing.low_dt, dt_2)

    def test_second_bar_close_above_first_high(self):
        dt_1 = datetime(2024, 1, 1)
        dt_2 = datetime(2024, 1, 2)

        self.swing.unpack(dict(high=100, low=90, high_dt=dt_1, low_dt=dt_1))
        self.swing.identify(dt_2, 105, 95, 102)

        self.assertEqual(self.swing.high, 105)
        self.assertEqual(self.swing.low, 90)
        self.assertEqual(self.swing.trend, "UP")

        self.assertEqual(self.swing.high_dt, dt_2)
        self.assertEqual(self.swing.low_dt, dt_1)

    def test_uptrend_new_high_with_no_sph(self):
        """SPH is not set, bar makes new high"""
        dt = datetime(2024, 1, 1)
        self.swing.unpack(dict(trend="UP", high=100))

        self.swing.identify(dt, high=105, low=95, close=103)

        self.assertEqual(self.swing.trend, "UP")
        self.assertEqual(self.swing.high, 105)
        self.assertEqual(self.swing.high_dt, dt)

        self.assertEqual(self.swing.low, 95)
        self.assertEqual(self.swing.low_dt, dt)

    def test_downtrend_new_low_with_no_spl(self):
        """SPL is not set, bar makes new low"""
        dt = datetime(2024, 1, 1)
        self.swing.unpack(dict(trend="DOWN", low=100))

        self.swing.identify(dt, high=105, low=95, close=95)

        self.assertEqual(self.swing.trend, "DOWN")
        self.assertEqual(self.swing.high, 105)
        self.assertEqual(self.swing.high_dt, dt)

        self.assertEqual(self.swing.low, 95)
        self.assertEqual(self.swing.low_dt, dt)

    def test_uptrend_new_sph_formation(self):
        """New SPH formation, bar fails to make new high"""

        dt_1 = datetime(2024, 1, 1)
        dt_2 = datetime(2023, 12, 2)
        self.swing.unpack(
            dict(
                trend="UP",
                high=100,
                low=90,
                high_dt=dt_2,
            )
        )

        self.swing.identify(dt_1, high=98, low=95, close=95)

        self.assertEqual(self.swing.sph, 100)
        self.assertEqual(self.swing.sph_dt, dt_2)
        self.assertEqual(self.swing.low, 95)

    def test_downtrend_new_spl_formation(self):
        """New SPL formation, bar fails to make new low"""

        dt_1 = datetime(2024, 1, 1)
        dt_2 = datetime(2023, 12, 2)
        self.swing.unpack(
            dict(
                trend="DOWN",
                high=100,
                low=90,
                low_dt=dt_2,
            )
        )

        self.swing.identify(dt_1, high=98, low=92, close=92)

        self.assertEqual(self.swing.spl, 90)
        self.assertEqual(self.swing.spl_dt, dt_2)
        self.assertEqual(self.swing.high, 98)

    def test_uptrend_reversal_to_downtrend(self):
        """Low breaks the coc on closing basis"""

        dt_1 = datetime(2024, 1, 1)
        dt_2 = datetime(2023, 12, 2)

        self.swing.unpack(
            dict(trend="UP", high=100, low=90, coc=85, high_dt=dt_2)
        )

        self.swing.identify(dt_1, high=95, low=82, close=82)

        self.assertEqual(self.swing.trend, "DOWN")
        self.assertEqual(self.swing.coc, 100)
        self.assertEqual(self.swing.coc_dt, dt_2)
        self.assertEqual(self.swing.low, 82)
        self.assertEqual(self.swing.low_dt, dt_1)

    def test_downtrend_reversal_to_uptrend(self):
        """High break the coc on closing basis"""

        dt_1 = datetime(2024, 1, 1)
        dt_2 = datetime(2023, 12, 2)

        self.swing.unpack(
            dict(trend="DOWN", high=100, low=90, coc=105, low_dt=dt_2)
        )

        self.swing.identify(dt_1, high=107, low=95, close=107)

        self.assertEqual(self.swing.trend, "UP")
        self.assertEqual(self.swing.coc, 90)
        self.assertEqual(self.swing.coc_dt, dt_2)
        self.assertEqual(self.swing.high, 107)
        self.assertEqual(self.swing.high_dt, dt_1)

    def test_on_reversal_callback_called_in_uptrend(self):
        """On reversal callback function is called if attached"""

        dt_1 = datetime(2024, 1, 1)
        dt_2 = datetime(2023, 12, 2)

        self.swing.unpack(
            dict(
                trend="UP",
                high=100,
                low=90,
                coc=85,
                high_dt=dt_2,
            )
        )

        mock = Mock(spec=lambda *args, **kwargs: None)

        self.swing.on_reversal = mock

        self.swing.identify(dt_1, high=95, low=82, close=82)

        mock.assert_called_once_with(
            self.swing, date=dt_1, close=82, reversal_level=85
        )

    def test_on_reversal_callback_called_in_downtrend(self):
        """On reversal callback function is called if attached"""

        dt_1 = datetime(2024, 1, 1)
        dt_2 = datetime(2023, 12, 2)

        self.swing.unpack(
            dict(trend="DOWN", high=100, low=90, coc=105, low_dt=dt_2)
        )

        mock = Mock(spec=lambda *args, **kwargs: None)

        self.swing.on_reversal = mock

        self.swing.identify(dt_1, high=107, low=95, close=107)

        mock.assert_called_once_with(
            self.swing, date=dt_1, close=107, reversal_level=105
        )

    def test_uptrend_new_high_with_close_below_sph(self):
        """New Bar high above SPH but close below SPH"""

        dt = datetime(2023, 12, 25)
        self.swing.unpack(
            dict(trend="UP", sph=100, high=100, low=90, low_dt=dt)
        )

        self.swing.identify(datetime(2024, 1, 1), high=105, low=95, close=99)

        self.assertEqual(self.swing.trend, "UP")
        self.assertEqual(self.swing.high, 105)
        self.assertEqual(self.swing.low, 90)
        self.assertEqual(self.swing.low_dt, dt)

    def test_downtrend_new_low_with_close_above_spl(self):
        """New Bar low below SPL but close above SPL."""

        dt = datetime(2023, 12, 25)
        self.swing.unpack(
            dict(trend="DOWN", spl=100, high=110, low=100, high_dt=dt)
        )

        self.swing.identify(datetime(2024, 1, 1), high=105, low=95, close=102)

        self.assertEqual(self.swing.trend, "DOWN")
        self.assertEqual(self.swing.low, 95)
        self.assertEqual(self.swing.high, 110)
        self.assertEqual(self.swing.high_dt, dt)

    def test_uptrend_continuation(self):
        """SPH is set and new SPH formed."""

        dt = datetime(2023, 12, 25)

        self.swing.unpack(
            dict(trend="UP", sph=100, high=100, low=90, low_dt=dt)
        )

        self.swing.identify(datetime(2024, 1, 1), high=103, low=95, close=102)

        self.assertIsNone(self.swing.sph)
        self.assertIsNone(self.swing.sph_dt)
        self.assertEqual(self.swing.coc, 90)
        self.assertEqual(self.swing.coc_dt, dt)

    def test_downtrend_continuation(self):
        """SPL is set and new SPL formed."""
        dt = datetime(2023, 12, 25)

        self.swing.unpack(
            dict(trend="DOWN", spl=100, high=110, low=95, high_dt=dt)
        )

        self.swing.identify(datetime(2024, 1, 1), high=103, low=93, close=93)

        self.assertIsNone(self.swing.spl)
        self.assertIsNone(self.swing.spl_dt)
        self.assertEqual(self.swing.coc, 110)
        self.assertEqual(self.swing.coc_dt, dt)

    def test_sph_broken_within_threshold(self):
        """SPH broken but retracement is within threshold, coc remains same and breakout is ignored."""

        dt = datetime(2023, 12, 25)

        self.swing.retrace_threshold_pct = 8

        self.swing.unpack(
            dict(
                trend="UP",
                sph=100,
                coc=90,
                high=105,
                low=95,
                low_dt=dt,
                coc_dt=dt,
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=106, low=95, close=102)

        self.assertEqual(self.swing.high, 106)
        self.assertEqual(self.swing.coc, 90)
        self.assertEqual(self.swing.coc_dt, dt)
        self.assertIsNone(self.swing.sph)

    def test_spl_broken_within_threshold(self):
        """SPL broken but retracement is within threshold, coc remains same and breakout is ignored."""

        dt = datetime(2023, 12, 25)

        self.swing.retrace_threshold = 8 / 100

        self.swing.unpack(
            dict(
                trend="DOWN",
                spl=100,
                coc=110,
                high=110,
                low=100,
                high_dt=dt,
                coc_dt=dt,
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=103, low=95, close=95)

        self.assertEqual(self.swing.low, 95)
        self.assertEqual(self.swing.coc, 110)
        self.assertEqual(self.swing.coc_dt, dt)
        self.assertIsNone(self.swing.spl)

    def test_sph_broken_exceeds_threshold(self):
        """SPH broken and retracement is above threshold"""

        dt = datetime(2023, 12, 25)

        self.swing.retrace_threshold = 3 / 100

        self.swing.unpack(
            dict(
                trend="UP",
                sph=100,
                coc=90,
                high=105,
                low=95,
                low_dt=dt,
                coc_dt=dt,
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=106, low=95, close=102)

        self.assertEqual(self.swing.high, 106)
        self.assertEqual(self.swing.coc, 95)
        self.assertEqual(self.swing.coc_dt, dt)
        self.assertIsNone(self.swing.sph)

    def test_on_breakout_callback_called_in_uptrend(self):
        """On breakout callback function is called if attached"""

        dt_1 = datetime(2023, 12, 25)
        dt_2 = datetime(2024, 1, 1)

        self.swing.unpack(dict(trend="UP", sph=100, low=95, low_dt=dt_1))

        mock = Mock(spec=lambda *args, **kwargs: None)

        self.swing.on_breakout = mock

        self.swing.identify(dt_2, high=106, low=95, close=102)

        mock.assert_called_once_with(
            self.swing, date=dt_2, close=102, breakout_level=100
        )

    def test_on_breakout_callback_called_in_downtrend(self):
        """On breakout callback function is called if attached"""

        dt_1 = datetime(2023, 12, 25)
        dt_2 = datetime(2024, 1, 1)

        self.swing.unpack(dict(trend="DOWN", spl=100, high=110, high_dt=dt_1))

        mock = Mock(spec=lambda *args, **kwargs: None)

        self.swing.on_breakout = mock

        self.swing.identify(dt_2, high=106, low=95, close=95)

        mock.assert_called_once_with(
            self.swing, date=dt_2, close=95, breakout_level=100
        )


if __name__ == "__main__":
    unittest.main()
