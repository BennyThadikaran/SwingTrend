# Swing

A mechanical approach to determine the trend of a stock along with breakout and reversal levels.

Python version: >= 3.8

If you ❤️ my work so far, please 🌟 this repo.

## 👽 Documentation

[https://bennythadikaran.github.io/SwingTrend](https://bennythadikaran.github.io/SwingTrend)

## Installation

`pip install swingtrend`

## Basic Usage

`from swingtrend import Swing`

To initialize with default setting:

`swing = Swing(retrace_threshold_pct=5, sideways_threshold=20, debug=False)`

See the documentation for more details.

## Inspiration

This work was inspired by youtube Channel **Matt Donlevey - Photon Trading**.

You can watch their video [How To Understand Market Structure](https://www.youtube.com/watch?v=Pd9ASRCHWmQ&t=251) to understand some of the concepts.

## How the class works

See [simple explanation of how the program works](https://bennythadikaran.github.io/SwingTrend/swing_algorithm.html)

To use the Photon method as explained in the video, instantiate the class as `Swing(retrace_threshold_pct=None)`

In the Photon method, both minor and major pivots can result in trend continuation or trend reversal. (This includes a single bar pullback).

I prefer avoiding the minor pivots by setting a minimum threshold percent. If the threshold is set to 8%, the pullback must retrace atleast 8% or more to be considered an important level for trend reversal or continuation.
