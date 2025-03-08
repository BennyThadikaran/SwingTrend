import unittest
from datetime import datetime

from context import Swing


class TestSwingLegCount(unittest.TestCase):
    """
    Following Cases covered in this unittest

    Trend is None, swing_leg_count is 0

    On break of structure, swing_leg_count is incremented
    On reversal, swing_leg_count is reset to 0
    """

    def setUp(self) -> None:
        self.swing = Swing(retrace_threshold_pct=None)

    def test_no_trend_count_is_zero(self):
        self.swing.unpack(dict(high=100, low=90))

        self.swing.identify(datetime(2024, 1, 1), high=97, low=95, close=95)
        self.swing.identify(datetime(2024, 1, 2), high=98, low=93, close=94)

        self.assertEqual(self.swing.leg_count, 0)

    def test_uptrend_sph_break_on_closing_basis(self):
        """New bar closes above SPH. Bar count is reset to 0"""
        self.swing.unpack(
            dict(
                trend="UP",
                sph=100,
                _Swing__leg_count=1,
                low_dt=datetime(2023, 12, 25),
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=105, low=95, close=103)

        self.assertEqual(self.swing.leg_count, 2)

    def test_downtrend_spl_break_on_closing_basis(self):
        """New bar closes below SPL. Bar count is reset to 0"""
        self.swing.unpack(
            dict(
                trend="DOWN",
                spl=100,
                _Swing__leg_count=1,
                low_dt=datetime(2023, 12, 25),
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=105, low=95, close=98)

        self.assertEqual(self.swing.leg_count, 2)

    def test_uptrend_to_downtrend_reversal(self):
        """Reversal to downtrend. Bar count is reset to 0"""
        self.swing.unpack(
            dict(
                trend="UP",
                sph=100,
                coc=95,
                _Swing__leg_count=5,
                high_dt=datetime(2023, 12, 26),
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=95, low=90, close=92)

        self.assertEqual(self.swing.leg_count, 0)

    def test_downtrend_to_uptrend_reversal(self):
        """Reversal to uptrend. Bar count is reset to 0"""
        self.swing.unpack(
            dict(
                trend="DOWN",
                spl=95,
                coc=100,
                _Swing__leg_count=5,
                low_dt=datetime(2023, 12, 26),
            )
        )

        self.swing.identify(datetime(2024, 1, 1), high=105, low=98, close=105)

        self.assertEqual(self.swing.leg_count, 0)


if __name__ == "__main__":
    unittest.main()
