import unittest
from datetime import datetime

from context import Swing


class TestSwingBarCount(unittest.TestCase):
    """
    Following Cases covered in this unittest

    - Trend is None, bars_since is 0

    In uptrend, bars_since is reset to 0, if:

    - SPH is set. New High but SPH not broken on closing basis.
    - SPH is set. SPH broken on closing basis.
    - SPH is None. New High (After reversal to uptrend)
    - New SPH has formed
    - On reversal to downtrend

    In downtrend, bars_since is reset to 0, if:

    - SPL is set. New Low but SPL not broken on closing basis.
    - SPL is set. SPL broken on closing basis.
    - SPL is None. New Low (After reversal to downtrend)
    - New SPL has formed
    - On reversal to uptrend

    In uptrend,

    - bar_since increments when SPH is set and bar fails to make new high
    - First SPH formed, bar_since increments to 1

    In downtrend

    - bar_since increments when SPL is set and bar fails to make new low
    - First SPL formed, bar_since increments to 1
    """

    def setUp(self) -> None:
        self.swing = Swing(retrace_threshold_pct=None)

    def test_no_trend_count_is_zero(self):
        self.swing.unpack(dict(high=100, low=90))

        self.swing.identify(datetime(2024, 1, 1), high=97, low=95, close=95)
        self.swing.identify(datetime(2024, 1, 2), high=98, low=93, close=94)

        self.assertEqual(self.swing.bars_since, 0)

    def test_uptrend_new_high_with_close_below_sph(self):
        """New Bar high above SPH but close below SPH. Bar count is reset to 0"""
        self.swing.unpack(
            dict(trend="UP", sph=100, high=100, _Swing__bars_since=5)
        )

        self.swing.identify(datetime(2024, 1, 1), high=105, low=95, close=99)

        self.assertEqual(self.swing.bars_since, 0)

    def test_downtrend_new_low_with_close_above_spl(self):
        """New Bar low below SPL but close above SPL. Bar count is reset to 0"""
        self.swing.unpack(
            dict(trend="DOWN", spl=100, low=100, _Swing__bars_since=5)
        )

        self.swing.identify(datetime(2024, 1, 1), high=105, low=95, close=102)

        self.assertEqual(self.swing.bars_since, 0)

    def test_uptrend_sph_break_on_closing_basis(self):
        """New bar closes above SPH. Bar count is reset to 0"""
        self.swing.unpack(
            dict(
                trend="UP",
                sph=100,
                _Swing__bars_since=5,
                low_dt=datetime(2023, 12, 25),
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=105, low=95, close=103)

        self.assertEqual(self.swing.bars_since, 0)

    def test_downtrend_spl_break_on_closing_basis(self):
        """New bar closes below SPL. Bar count is reset to 0"""
        self.swing.unpack(
            dict(
                trend="DOWN",
                spl=100,
                _Swing__bars_since=5,
                low_dt=datetime(2023, 12, 25),
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=105, low=95, close=98)

        self.assertEqual(self.swing.bars_since, 0)

    def test_uptrend_new_high_with_no_sph(self):
        """No SPH formed but new high. Bar count is reset to 0"""
        self.swing.unpack(dict(trend="UP", high=100, _Swing__bars_since=5))

        self.swing.identify(datetime(2024, 1, 1), high=105, low=95, close=103)

        self.assertEqual(self.swing.bars_since, 0)

    def test_downtrend_new_low_with_no_spl(self):
        """No SPL formed but new low. Bar count is reset to 0"""
        self.swing.unpack(dict(trend="DOWN", low=100, _Swing__bars_since=5))

        self.swing.identify(datetime(2024, 1, 1), high=105, low=95, close=103)

        self.assertEqual(self.swing.bars_since, 0)

    def test_uptrend_continuation(self):
        """SPH is set and new SPH formed. Bar count is reset to 0"""
        self.swing.unpack(
            dict(trend="UP", sph=100, high=105, _Swing__bars_since=5)
        )

        self.swing.identify(datetime(2024, 1, 1), high=103, low=95, close=102)

        self.assertEqual(self.swing.bars_since, 0)

    def test_downtrend_continuation(self):
        """SPL is set and new SPL formed. Bar count is reset to 0"""
        self.swing.unpack(
            dict(trend="DOWN", spl=100, low=95, _Swing__bars_since=5)
        )

        self.swing.identify(datetime(2024, 1, 1), high=103, low=93, close=93)

        self.assertEqual(self.swing.bars_since, 0)

    def test_uptrend_to_downtrend_reversal(self):
        """Reversal to downtrend. Bar count is reset to 0"""
        self.swing.unpack(
            dict(
                trend="UP",
                sph=100,
                coc=95,
                _Swing__bars_since=5,
                high_dt=datetime(2023, 12, 26),
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=95, low=90, close=92)

        self.assertEqual(self.swing.trend, "DOWN")
        self.assertEqual(self.swing.bars_since, 0)

    def test_downtrend_to_uptrend_reversal(self):
        """Reversal to uptrend. Bar count is reset to 0"""
        self.swing.unpack(
            dict(
                trend="DOWN",
                spl=95,
                coc=100,
                _Swing__bars_since=5,
                low_dt=datetime(2023, 12, 26),
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=105, low=98, close=105)

        self.assertEqual(self.swing.trend, "UP")
        self.assertEqual(self.swing.bars_since, 0)

    def test_uptrend_bar_below_sph(self):
        """Bar high below SPH. Bar count is incremented."""

        self.swing.unpack(
            dict(trend="UP", sph=100, coc=90, _Swing__bars_since=5)
        )

        self.swing.identify(datetime(2024, 1, 1), high=98, low=95, close=96)

        self.assertEqual(self.swing.bars_since, 6)

    def test_downtrend_bar_above_spl(self):
        """Bar low above SPL. Bar count is incremented."""

        self.swing.unpack(
            dict(trend="DOWN", spl=100, coc=110, _Swing__bars_since=5)
        )

        self.swing.identify(datetime(2024, 1, 1), high=105, low=102, close=102)

        self.assertEqual(self.swing.bars_since, 6)

    def test_uptrend_bar_above_spl(self):
        """Bar low above SPL. Bar count is incremented."""

        self.swing.unpack(
            dict(trend="DOWN", spl=100, coc=110, _Swing__bars_since=5)
        )

        self.swing.identify(datetime(2024, 1, 1), high=105, low=102, close=102)

        self.assertEqual(self.swing.bars_since, 6)

    def test_uptrend_first_sph(self):
        """First SPH formed in uptrend. Bar count is set to 1."""

        self.swing.unpack(
            dict(
                trend="UP",
                high=105,
                _Swing__bars_since=0,
                high_dt=datetime(2024, 12, 25),
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=103, low=98, close=103)

        self.assertEqual(self.swing.bars_since, 1)

    def test_downtrend_first_spl(self):
        """First SPL formed in downtrend. Bar count is set to 1."""

        self.swing.unpack(
            dict(
                trend="DOWN",
                low=100,
                _Swing__bars_since=0,
                low_dt=datetime(2024, 12, 25),
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=106, low=102, close=102)

        self.assertEqual(self.swing.bars_since, 1)


if __name__ == "__main__":
    unittest.main()
