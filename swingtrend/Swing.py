import logging
from datetime import datetime
from typing import Callable, Literal, Optional

# logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)
#
# logger = logging.getLogger(__name__)


class Swing:
    """
    A class to help determine the current trend of an Stock.

    ``Swing.trend: str or None`` - A string indicating the current trend. UP or DOWN or None. Trend will be None if too few candles were provided.

    ``Swing.sph: float or None`` - Swing high indicating the current breakout level to maintain uptrend. If trend is DOWN or None, SPH is None

    ``Swing.spl: float or None`` - Swing low indicating the current breakdown level to maintain downtrend. If trend is UP or None, SPL is None

    ``Swing.sph_dt`` and ``Swing.spl_dt`` are the relevant dates for the current SPH and SPL in the DataFrame. They will be None if SPL or SPH is None.

    ``Swing.coc: float or None`` - Change of Character (CoCh) or Reversal level. If this level is broken, current trend will be reversed.

    :param retrace_threshold_pct: Default 5.0. Minimum retracement required to qualify a Change of Character (CoCh) level. If None, all retracements qualify.
    :type retrace_threshold_pct: float or None
    :param sideways_threshold: Default 20. Minimum number of bars after which the trend is considered range-bound or sideways.
    :type sideways_threshold: int
    :param debug: Default False. Print additional logs for debug purposes.
    :type debug: bool
    """

    trend: Optional[Literal["UP", "DOWN"]] = None

    df = None

    high = low = coc = sph = spl = retrace_threshold_pct = None

    coc_dt = sph_dt = spl_dt = retrace_threshold = None

    symbol: Optional[str] = None

    on_reversal: Optional[Callable] = None
    on_breakout: Optional[Callable] = None

    def __init__(
        self,
        retrace_threshold_pct: Optional[float] = 5.0,
        sideways_threshold: int = 20,
        debug=False,
    ):

        if retrace_threshold_pct:
            self.retrace_threshold = retrace_threshold_pct / 100

        self.sideways_threshold = sideways_threshold

        self.logger = logging.getLogger(__name__)

        if debug:
            self.logger.setLevel(logging.DEBUG)

        self.plot = False
        self.__bars_since = 0

    def is_sideways(self) -> bool:
        """
        Returns True if the instrument is range bound or sideways trend.

        **Note** ``swing.trend`` can be UP or DOWN and still be sideways. The trend only changes on Break of structure or reversal (break of CoCh).

        The instrument is considered sideways, if the number of bars since the last SPH or SPL was formed exceeds 20

        If a break of structure occurs or a trend reversal the bar count is reset to 0 until a new SPH or SPL is formed.
        """
        return self.__bars_since > self.sideways_threshold

    def run(self, sym: str, df, plot_lines=False, add_series=False):
        """
        Iterates through the DataFrame and determines the current trend of the instrument.

        Optionally it also records CoCh levels for plotting in Matplotlib. Use `plot_lines`.

        To add the current trend data to the pandas Dataframe, use `add_series`

        :param sym: Symbol name of the instrument.
        :type sym: str
        :param df: DataFrame containing OHLC data with DatetimeIndex
        :type df: pandas.DataFrame
        :param plot_lines: Default False. Generate line data marking CoCh levels to plot in Matplotlib
        :type plot_lines: bool
        :param add_series: Default False. If True, adds a Trend column to the DataFrame. 1 indicates UP, 0 indicates DOWN.
        :type add_series: bool
        """
        self.symbol = sym

        if plot_lines:
            self.plot = True
            self.plot_colors = []
            self.plot_lines = []
            self.df = df

        if add_series:
            df["TREND"] = 0

        for t in df.itertuples(name=None):
            dt, _, H, L, C, *_ = t

            self.identify(dt, H, L, C)

            if add_series and self.trend == "UP":
                df.loc[dt, "TREND"] = 1

    def identify(self, dt: datetime, high: float, low: float, close: float):
        """
        Identify the trend with the current OHLC data.
        """
        if self.trend is None:
            if self.high is None or self.low is None:
                self.high = high
                self.low = low
                self.high_dt = self.low_dt = dt
                self.logger.debug(f"{dt}: First Candle: High {high} Low: {low}")
                return

            # Set the trend when first bar high or low is broken
            if close > self.high:
                self.trend = "UP"
                self.high = high
                self.high_dt = dt
                self.coc = self.low
                self.coc_dt = self.low_dt

                self.logger.debug(f"{dt}: Start Trend: UP High: {high}")

            elif close < self.low:
                self.trend = "DOWN"
                self.low = low
                self.low_dt = dt
                self.coc = self.high
                self.coc_dt = self.high_dt

                self.logger.debug(f"{dt}: Start Trend: DOWN Low: {low}")

            if high > self.high:
                self.high = high
                self.high_dt = dt

            if low < self.low:
                self.low = low
                self.low_dt = dt

            return

        if self.trend == "UP":
            if self.sph:
                self.__bars_since += 1

                if self.high and high > self.high:
                    self.high = high
                    self.high_dt = dt

                if self.low is None or low < self.low:
                    self.low = low
                    self.low_dt = dt

                if close > self.sph:
                    retrace_pct = (self.low - self.sph) / self.sph

                    sph = self.sph
                    self.sph = self.sph_dt = None
                    self.__bars_since = 0

                    if (
                        self.retrace_threshold
                        and abs(retrace_pct) < self.retrace_threshold
                    ):
                        return

                    self.coc = self.low
                    self.coc_dt = self.low_dt

                    self.logger.debug(
                        f"{dt}: BOS UP CoCh: {self.coc} Retrace: {retrace_pct:.2%}"
                    )

                    if self.plot:
                        line_end_dt = self.__line_end_dt(self.coc_dt)

                        self.plot_lines.append(
                            (
                                (self.coc_dt, self.coc),
                                (line_end_dt, self.coc),
                            )
                        )
                        self.plot_colors.append("g")

                    if self.on_breakout:
                        self.on_breakout(
                            self.symbol,
                            dt,
                            self.trend,
                            close,
                            sph,
                            self.coc,
                        )
                    return

            if self.high and high > self.high:
                self.high = high
                self.high_dt = dt
                self.low = low
                self.low_dt = dt
                self.logger.debug(f"{dt}: New High: {high}")
            else:
                if self.sph is None:
                    self.sph = self.high
                    self.sph_dt = self.high_dt
                    self.low = self.low_dt = None
                    self.__bars_since = 0

                    self.logger.debug(
                        f"{dt}: Swing High - UP SPH: {self.sph} CoCh: {self.coc}"
                    )

                if self.low is None or low < self.low:
                    self.low = low
                    self.low_dt = dt
                    self.__bars_since += 1

                if self.coc and close < self.coc:
                    price_level = self.coc
                    self.__switch_downtrend(dt, low)

                    if self.on_reversal:
                        self.on_reversal(
                            self.symbol,
                            dt,
                            self.trend,
                            close,
                            self.coc,
                            price_level,
                        )
            return

        if self.trend == "DOWN":
            if self.spl:
                self.__bars_since += 1

                if self.low and low < self.low:
                    self.low = low
                    self.low_dt = dt

                if self.high is None or high > self.high:
                    self.high = high
                    self.high_dt = dt

                if close < self.spl:
                    retrace_pct = (self.high - self.spl) / self.spl

                    spl = self.spl
                    self.spl = self.spl_dt = None
                    self.__bars_since = 0

                    if (
                        self.retrace_threshold
                        and retrace_pct < self.retrace_threshold
                    ):
                        return

                    self.coc = self.high
                    self.coc_dt = self.high_dt
                    self.logger.debug(f"{dt}: BOS DOWN CoCh: {self.coc}")

                    if self.plot:
                        line_end_dt = self.__line_end_dt(self.coc_dt)

                        self.plot_lines.append(
                            (
                                (self.coc_dt, self.coc),
                                (line_end_dt, self.coc),
                            )
                        )

                        self.plot_colors.append("r")

                    if self.on_breakout:
                        self.on_breakout(
                            self.symbol,
                            dt,
                            self.trend,
                            close,
                            spl,
                            self.coc,
                        )
                    return

            if self.low and low < self.low:
                self.low = low
                self.high = high
                self.low_dt = self.high_dt = dt
                self.logger.debug(f"{dt}: New Low: {low}")
            else:
                if self.spl is None:
                    self.spl = self.low
                    self.spl_dt = self.low_dt
                    self.high = self.high_dt = None
                    self.__bars_since = 0

                    self.logger.debug(
                        f"{dt}: Swing Low - DOWN SPL: {self.spl} CoCh: {self.coc}"
                    )

                if self.high is None or high > self.high:
                    self.high = high
                    self.high_dt = dt
                    self.__bars_since += 1

                if self.coc and close > self.coc:
                    price_level = self.coc
                    self.__switch_uptrend(dt, high)

                    if self.on_reversal:
                        self.on_reversal(
                            self.symbol,
                            dt,
                            self.trend,
                            close,
                            self.coc,
                            price_level,
                        )

    def reset(self):
        """Reset all properties. Used when switching to a different stock / symbol."""

        self.high = self.low = self.trend = self.coc = self.sph = self.spl = (
            self.high_dt
        ) = self.low_dt = self.coc_dt = self.sph_dt = self.spl_dt = None

        self.__bars_since = 0

        if self.plot:
            self.df = None
            self.plot_colors.clear()
            self.plot_lines.clear()

    def pack(self) -> dict:
        """
        Get the dictionary representation of the class for serialization purposes.

        Used to store the current state of the class, so as to resume later
        """
        dct = self.__dict__.copy()

        # Remove non serializable objects
        del dct["logger"]

        if "on_reversal" in dct:
            del dct["on_reversal"]

        if "on_breakout" in dct:
            del dct["on_breakout"]

        return dct

    def unpack(self, data: dict):
        """
        Update the class with data from the dictionary.

        Used to restore a previously saved state and resume operations.

        :param data: Dictionary data obtained from Swing.pack.
        :type data: dict
        """
        self.__dict__.update(data)

    def __line_end_dt(self, dt):
        if self.df is None:
            raise ValueError("DataFrame not found.")

        idx = self.df.index.get_loc(dt)

        if isinstance(idx, slice):
            idx = idx.stop

        idx = min(int(idx) + 15, len(self.df) - 1)
        return self.df.index[idx]

    def __switch_downtrend(self, dt: datetime, low: float):
        self.trend = "DOWN"
        self.coc = self.high
        self.coc_dt = self.high_dt
        self.high = self.sph = self.sph_dt = None
        self.low = low
        self.low_dt = dt
        self.__bars_since = 0

        if self.plot:
            line_end_dt = self.__line_end_dt(self.coc_dt)

            self.plot_lines.append(
                (
                    (self.coc_dt, self.coc),
                    (line_end_dt, self.coc),
                )
            )

            self.plot_colors.append("r")

        self.logger.debug(
            f"{dt}: Reversal {self.trend} Low: {self.low} CoCh: {self.coc}"
        )

    def __switch_uptrend(self, dt: datetime, high: float):
        self.trend = "UP"
        self.coc = self.low
        self.coc_dt = self.low_dt
        self.low = self.spl = self.spl_dt = None
        self.high = high
        self.high_dt = dt
        self.__bars_since = 0

        if self.plot:
            line_end_dt = self.__line_end_dt(self.coc_dt)

            self.plot_lines.append(
                ((self.coc_dt, self.coc), (line_end_dt, self.coc))
            )

            self.plot_colors.append("g")

        self.logger.debug(
            f"{dt}: Reversal {self.trend} High: {self.high} CoCh: {self.coc}"
        )
