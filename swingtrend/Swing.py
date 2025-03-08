import logging
from typing import Callable, Literal, Optional


class Swing:
    """
    A class to help determine the current trend of an Stock.

    :param retrace_threshold_pct: Default 5.0. Minimum retracement required to qualify a Change of Character (CoCh) level. If None, all retracements qualify.
    :type retrace_threshold_pct: float or None
    :param sideways_threshold: Default 20. Minimum number of bars after which the trend is considered range-bound or sideways.
    :type sideways_threshold: int
    :param minimum_bar_count: Default 40. Minimum number of bars required to accurately determine trend.
    :type minimum_bar_count: int
    :param debug: Default False. Print additional logs for debug purposes.
    :type debug: bool
    """

    trend: Optional[Literal["UP", "DOWN"]] = None

    df = None

    high = low = coc = sph = spl = None

    coc_dt = sph_dt = spl_dt = __retrace_threshold = None

    symbol: Optional[str] = None

    on_reversal: Optional[Callable] = None
    on_breakout: Optional[Callable] = None

    def __init__(
        self,
        retrace_threshold_pct: Optional[float] = 5.0,
        sideways_threshold: int = 20,
        minimum_bar_count: int = 40,
        debug=False,
    ):

        if retrace_threshold_pct:
            self.retrace_threshold_pct = retrace_threshold_pct

        self.sideways_threshold = sideways_threshold

        self.logger = logging.getLogger(__name__)

        if debug:
            self.logger.setLevel(logging.DEBUG)

        self.minimum_bar_count = minimum_bar_count

        self.plot = False
        self.__bars_since = 0
        self.__total_bar_count = 0
        self.__leg_count = 0

    @property
    def bars_since(self) -> int:
        """
        .. versionadded:: 2.0.0

        Bar count since last swing high or low.

        :type: int
        """
        return self.__bars_since

    @property
    def is_trend_stable(self) -> bool:
        """
        .. versionadded:: 2.0.0

        Have enough bars been accumulated to accurately determine the trend?

        :type: bool
        """
        return self.__total_bar_count > self.minimum_bar_count

    @property
    def is_sideways(self) -> bool:
        """
        .. versionadded:: 2.0.0

        Is the instrument range bound or in a sideways trend?

        The instrument is considered sideways, if the number of bars since the last SPH or SPL was formed exceeds ``Swing.sideways_threshold``

        **Note** ``swing.trend`` can be UP or DOWN and still be sideways. The trend changes only on breakout or reversal.

        If a breakout or trend reversal occurs, the bar count is reset to 0, until a new SPH or SPL is formed.

        :type: bool
        """
        return self.__bars_since > self.sideways_threshold

    @property
    def leg_count(self) -> int:
        """
        .. versionadded:: 2.0.1

        Number of swing legs, the trend has completed.

        - Reset to zero on trend reversal.
        - Incremented on break of structure.
        """
        return self.__leg_count

    @property
    def retrace_threshold_pct(self) -> Optional[float]:
        """Retrace threshold percent. Minimum retracement required to qualify a Change of Character (CoCh) level.

        :setter: Sets the retrace threshold percent
        :type: float or None
        """
        if self.__retrace_threshold:
            return self.__retrace_threshold * 100
        return None

    @retrace_threshold_pct.setter
    def retrace_threshold_pct(self, value: Optional[float]):
        """
        Set the retrace threshold percent.
        """
        self.__retrace_threshold = value / 100 if value else None

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
        :param add_series: Default False. If True, adds a `TREND` and `IS_SIDEWAYS` column to the DataFrame. 1 if TREND is UP or in sideways range, 0 otherwise.
        :type add_series: bool
        """
        self.symbol = sym
        self.df = df

        if plot_lines:
            self.plot = True
            self.plot_colors = []
            self.plot_lines = []
            self.df = df

        if add_series:
            df["TREND"] = None
            df["IS_SIDEWAYS"] = None

        for t in df.itertuples(name=None):
            dt, _, H, L, C, *_ = t

            self.identify(dt, H, L, C)

            if add_series:
                if self.is_trend_stable:
                    df.loc[dt, "TREND"] = int(self.trend == "UP")
                    df.loc[dt, "IS_SIDEWAYS"] = int(self.is_sideways)

    def identify(self, date, high: float, low: float, close: float) -> None:
        """
        Identify the trend with the current OHLC data.

        :param date: datetime of the candle
        :type date: str or datetime
        :param high: Candle high
        :type high: float
        :param low: Candle low
        :type low: float
        :param close: Candle close
        :type close: float
        """
        self.__total_bar_count += 1

        if self.trend is None:
            if self.high is None or self.low is None:
                self.high = high
                self.low = low
                self.high_dt = self.low_dt = date
                self.logger.debug(
                    f"{date}: First Candle: High {high} Low: {low}"
                )
                return

            # Set the trend when first bar high or low is broken
            if close > self.high:
                self.trend = "UP"
                self.high = high
                self.high_dt = date
                self.coc = self.low
                self.coc_dt = self.low_dt

                self.logger.debug(f"{date}: Start Trend: UP High: {high}")

            elif close < self.low:
                self.trend = "DOWN"
                self.low = low
                self.low_dt = date
                self.coc = self.high
                self.coc_dt = self.high_dt

                self.logger.debug(f"{date}: Start Trend: DOWN Low: {low}")

            if high > self.high:
                self.high = high
                self.high_dt = date

            if low < self.low:
                self.low = low
                self.low_dt = date

            return

        if self.trend == "UP":
            # Increment bar count on every bar
            # Reset count, if SPH is broken or reversal to downtrend
            # or new highs are being formed.
            self.__bars_since += 1

            if self.sph:
                if self.high and high > self.high:
                    self.__bars_since = 0
                    self.high = high
                    self.high_dt = date

                if self.low is None or low < self.low:
                    self.low = low
                    self.low_dt = date

                if close > self.sph:
                    retrace_pct = (self.low - self.sph) / self.sph

                    sph = self.sph
                    self.sph = self.sph_dt = None
                    self.__bars_since = 0

                    if (
                        self.__retrace_threshold
                        and abs(retrace_pct) < self.__retrace_threshold
                    ):
                        return

                    self.coc = self.low
                    self.coc_dt = self.low_dt
                    self.__leg_count += 1

                    self.logger.debug(
                        f"{date}: BOS UP CoCh: {self.coc} Retrace: {retrace_pct:.2%}"
                    )

                    if self.plot:
                        line_end_dt = self.__line_end_dt(self.coc_dt)

                        self.plot_lines.append(
                            ((self.coc_dt, self.coc), (line_end_dt, self.coc))
                        )
                        self.plot_colors.append("g")

                    if self.on_breakout:
                        self.on_breakout(
                            self,
                            date=date,
                            close=close,
                            breakout_level=sph,
                        )
                    return

            if self.high and high > self.high:
                self.__bars_since = 0
                self.high = high
                self.high_dt = date
                self.low = low
                self.low_dt = date
                self.logger.debug(f"{date}: New High: {high}")
            else:
                if self.sph is None:
                    self.sph = self.high
                    self.sph_dt = self.high_dt
                    self.low = self.low_dt = None
                    self.__bars_since = 1  # reset but count the current bar

                    self.logger.debug(
                        f"{date}: Swing High - UP SPH: {self.sph} CoCh: {self.coc}"
                    )

                if self.low is None or low < self.low:
                    self.low = low
                    self.low_dt = date

                if self.coc and close < self.coc:
                    price_level = self.coc
                    self.__switch_downtrend(date, low)

                    if self.on_reversal:
                        self.on_reversal(
                            self,
                            date=date,
                            close=close,
                            reversal_level=price_level,
                        )
            return

        if self.trend == "DOWN":
            # Increment bar count on every bar
            # Reset count, if SPL is broken or reversal to downtrend
            # or new lows are being formed.
            self.__bars_since += 1

            if self.spl:

                if self.low and low < self.low:
                    self.__bars_since = 0
                    self.low = low
                    self.low_dt = date

                if self.high is None or high > self.high:
                    self.high = high
                    self.high_dt = date

                if close < self.spl:
                    retrace_pct = (self.high - self.spl) / self.spl

                    spl = self.spl
                    self.spl = self.spl_dt = None
                    self.__bars_since = 0

                    if (
                        self.__retrace_threshold
                        and retrace_pct < self.__retrace_threshold
                    ):
                        return

                    self.coc = self.high
                    self.coc_dt = self.high_dt
                    self.__leg_count += 1

                    self.logger.debug(f"{date}: BOS DOWN CoCh: {self.coc}")

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
                            self,
                            date=date,
                            close=close,
                            breakout_level=spl,
                        )
                    return

            if self.low and low < self.low:
                self.__bars_since = 0
                self.low = low
                self.high = high
                self.low_dt = self.high_dt = date
                self.logger.debug(f"{date}: New Low: {low}")
            else:
                if self.spl is None:
                    self.spl = self.low
                    self.spl_dt = self.low_dt
                    self.high = self.high_dt = None
                    self.__bars_since = 1  # reset but count the current bar

                    self.logger.debug(
                        f"{date}: Swing Low - DOWN SPL: {self.spl} CoCh: {self.coc}"
                    )

                if self.high is None or high > self.high:
                    self.high = high
                    self.high_dt = date

                if self.coc and close > self.coc:
                    price_level = self.coc
                    self.__switch_uptrend(date, high)

                    if self.on_reversal:
                        self.on_reversal(
                            self,
                            date=date,
                            close=close,
                            reversal_level=price_level,
                        )

    def reset(self) -> None:
        """Reset all properties. Used when switching to a different stock / symbol."""

        self.high = self.low = self.trend = self.coc = self.sph = self.spl = (
            self.high_dt
        ) = self.low_dt = self.coc_dt = self.sph_dt = self.spl_dt = self.df = (
            None
        )

        self.__bars_since = 0
        self.__total_bar_count = 0
        self.__leg_count = 0

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

        if "df" in dct:
            del dct["df"]

        if "on_reversal" in dct:
            del dct["on_reversal"]

        if "on_breakout" in dct:
            del dct["on_breakout"]

        return dct

    def unpack(self, data: dict) -> None:
        """
        Update the class with data from the dictionary.

        Used to restore a previously saved state and resume operations.

        :param data: Dictionary data obtained from Swing.pack.
        :type data: dict
        """
        self.__dict__.update(data)

    def __line_end_dt(self, date):
        if self.df is None:
            raise ValueError("DataFrame not found.")

        idx = self.df.index.get_loc(date)

        if isinstance(idx, slice):
            idx = idx.stop

        idx = min(int(idx) + 15, len(self.df) - 1)
        return self.df.index[idx]

    def __switch_downtrend(self, date, low: float):
        self.trend = "DOWN"
        self.coc = self.high
        self.coc_dt = self.high_dt
        self.high = self.sph = self.sph_dt = None
        self.low = low
        self.low_dt = date
        self.__bars_since = 0
        self.__leg_count = 0

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
            f"{date}: Reversal {self.trend} Low: {self.low} CoCh: {self.coc}"
        )

    def __switch_uptrend(self, date, high: float):
        self.trend = "UP"
        self.coc = self.low
        self.coc_dt = self.low_dt
        self.low = self.spl = self.spl_dt = None
        self.high = high
        self.high_dt = date
        self.__bars_since = 0
        self.__leg_count = 0

        if self.plot:
            line_end_dt = self.__line_end_dt(self.coc_dt)

            self.plot_lines.append(
                ((self.coc_dt, self.coc), (line_end_dt, self.coc))
            )

            self.plot_colors.append("g")

        self.logger.debug(
            f"{date}: Reversal {self.trend} High: {self.high} CoCh: {self.coc}"
        )
