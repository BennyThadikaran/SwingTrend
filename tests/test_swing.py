import unittest
from datetime import datetime, timedelta

from context import Swing


class TestSwing(unittest.TestCase):
    def setUp(self) -> None:
        self.swing = Swing(retrace_threshold_pct=None)

    def test_pack(self):
        self.swing.on_breakout = self.swing.on_reversal = print

        dct = self.swing.pack()
        self.assertIsInstance(dct, dict)

        # No callables or logger objects in dict
        self.assertNotIn("on_reversal", dct)
        self.assertNotIn("on_breakout", dct)
        self.assertNotIn("logger", dct)

    def test_first_candle(self):
        dt = datetime(2024, 1, 1)
        self.swing.identify(dt, 105.0, 90, 100)

        self.assertEqual(self.swing.high, 105)
        self.assertEqual(self.swing.low, 90)
        self.assertIsNone(self.swing.trend)

        self.assertEqual(self.swing.high_dt, dt)
        self.assertEqual(self.swing.low_dt, dt)

    def test_second_candle_close_low(self):
        dt_1 = datetime(2024, 1, 2)
        dt_2 = dt_1 + timedelta(1)

        self.swing.unpack(dict(high=105, low=90, high_dt=dt_1, low_dt=dt_1))
        self.swing.identify(dt_2, 100, 85, 88)

        self.assertEqual(self.swing.high, 105)
        self.assertEqual(self.swing.low, 85)
        self.assertEqual(self.swing.trend, "DOWN")

        self.assertEqual(self.swing.high_dt, dt_1)
        self.assertEqual(self.swing.low_dt, dt_2)

    def test_second_candle_close_high(self):
        dt_1 = datetime(2024, 1, 2)
        dt_2 = dt_1 + timedelta(1)

        self.swing.unpack(dict(high=105, low=90, high_dt=dt_1, low_dt=dt_1))
        self.swing.identify(dt_2, 110, 95, 108)

        self.assertEqual(self.swing.high, 110)
        self.assertEqual(self.swing.low, 90)
        self.assertEqual(self.swing.trend, "UP")

        self.assertEqual(self.swing.high_dt, dt_2)
        self.assertEqual(self.swing.low_dt, dt_1)

    def test_second_candle_outside_bar(self):
        dt_1 = datetime(2024, 1, 1)

        self.swing.unpack(dict(high=105, low=90, high_dt=dt_1, low_dt=dt_1))
        self.swing.identify(datetime(2024, 1, 2), 110, 85, 95)

        self.assertEqual(self.swing.high, 110)
        self.assertEqual(self.swing.low, 85)
        self.assertIsNone(self.swing.trend)

    def test_consecutive_highs(self):
        ohlc = (
            (datetime(2024, 1, 1), 100, 90, 98),
            (datetime(2024, 1, 2), 105, 95, 103),
            (datetime(2024, 1, 3), 110, 100, 108),
            (datetime(2024, 1, 4), 115, 105, 113),
        )

        for t in ohlc:
            self.swing.identify(*t)

        self.assertEqual(self.swing.high, 115)
        self.assertEqual(self.swing.low, 105)
        self.assertEqual(self.swing.trend, "UP")

    def test_consecutive_lows(self):
        ohlc = (
            (datetime(2024, 1, 1), 100, 90, 93),
            (datetime(2024, 1, 2), 95, 85, 88),
            (datetime(2024, 1, 3), 90, 80, 83),
            (datetime(2024, 1, 4), 85, 75, 78),
        )

        for t in ohlc:
            self.swing.identify(*t)

        self.assertEqual(self.swing.high, 85)
        self.assertEqual(self.swing.low, 75)
        self.assertEqual(self.swing.trend, "DOWN")

    def test_first_spl(self):
        ohlc = (
            (datetime(2024, 1, 1), 100, 90, 93),
            (datetime(2024, 1, 2), 95, 85, 88),
            (datetime(2024, 1, 3), 90, 80, 83),
            (datetime(2024, 1, 4), 85, 75, 78),
        )

        for t in ohlc:
            self.swing.identify(*t)

        self.swing.identify(datetime(2024, 1, 5), 87, 78, 80)
        self.assertEqual(self.swing.spl, 75)
        self.assertEqual(self.swing.coc, 100)

    def test_first_sph(self):
        ohlc = (
            (datetime(2024, 1, 1), 100, 90, 98),
            (datetime(2024, 1, 2), 105, 95, 103),
            (datetime(2024, 1, 3), 110, 100, 108),
            (datetime(2024, 1, 4), 115, 105, 113),
        )

        for t in ohlc:
            self.swing.identify(*t)

        self.swing.identify(datetime(2024, 1, 5), 112, 108, 110)
        self.assertEqual(self.swing.sph, 115)
        self.assertEqual(self.swing.coc, 90)

    def test_reversal_attempt_closed_above(self):
        """Low below CoC but closed above, trend remains UP"""

        self.swing.unpack(dict(trend="UP", sph=110, high=110, low=100, coc=90))

        self.swing.identify(datetime(2024, 12, 1), high=95, low=85, close=92)

        self.assertEqual(self.swing.trend, "UP")
        self.assertEqual(self.swing.low, 85)
        self.assertEqual(self.swing.high, 110)
        self.assertEqual(self.swing.coc, 90)

    def test_reversal_down(self):
        """Close below CoC , trend reversal Down"""

        self.swing.unpack(
            dict(
                trend="UP",
                sph=110,
                high=110,
                low=100,
                coc=90,
                high_dt=datetime(2024, 12, 1),
            )
        )

        self.swing.identify(datetime(2024, 12, 2), high=95, low=85, close=88)

        self.assertEqual(self.swing.trend, "DOWN")
        self.assertEqual(self.swing.low, 85)
        self.assertIsNone(self.swing.high)
        self.assertEqual(self.swing.coc, 110)

    def test_reversal_up(self):
        """Close above CoC , trend reversal UP"""

        self.swing.unpack(
            dict(
                trend="DOWN",
                spl=90,
                low=90,
                high=105,
                coc=110,
                low_dt=datetime(2024, 12, 1),
            )
        )

        self.swing.identify(datetime(2024, 12, 2), high=115, low=100, close=112)

        self.assertEqual(self.swing.trend, "UP")
        self.assertIsNone(self.swing.low)
        self.assertEqual(self.swing.high, 115)
        self.assertEqual(self.swing.coc, 90)

    def test_trend_continuation_up(self):
        """Close above SPH, trend continues UP"""

        self.swing.unpack(
            dict(
                trend="UP",
                sph=110,
                high=110,
                low=100,
                coc=90,
                low_dt=datetime(2024, 12, 1),
            )
        )

        self.swing.identify(datetime(2024, 12, 2), high=115, low=105, close=112)

        self.assertEqual(self.swing.trend, "UP")
        self.assertEqual(self.swing.high, 115)
        self.assertEqual(self.swing.low, 100)
        self.assertEqual(self.swing.coc, 100)

    def test_trend_continuation_down(self):
        """Close above SPH, trend continues UP"""

        self.swing.unpack(
            dict(
                trend="DOWN",
                spl=90,
                low=90,
                high=105,
                coc=110,
                high_dt=datetime(2024, 12, 1),
            )
        )

        self.swing.identify(datetime(2024, 12, 2), high=102, low=85, close=88)

        self.assertEqual(self.swing.trend, "DOWN")
        self.assertEqual(self.swing.high, 105)
        self.assertEqual(self.swing.low, 85)
        self.assertEqual(self.swing.coc, 105)


if __name__ == "__main__":
    unittest.main()
