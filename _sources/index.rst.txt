.. Swing documentation master file, created by
   sphinx-quickstart on Tue Feb 25 17:06:20 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Swing documentation
===================

The ``Swing`` class uses a mechanical approach to determine the trend of a stock along with breakout and reversal levels.

Python version: >= 3.8

No external dependencies are required.

Pandas and Mplfinance are optional requirements depending on your usage and requirement.

See this youtube video: [How To Understand Market Structure](https://www.youtube.com/watch?v=Pd9ASRCHWmQ&t=251)

.. code-block:: python

  Uptrend Continuation

                 /
  _____________ /<-- Break of Structure (BOS)
  \ MARKET     /       (Breakout level)
   \STRUCTURE /
    \  /\    /
     \/  \  /
          \/______<--- Change of Structure (CoCh)
                        (Reversal level)

.. code-block:: python

   Downtrend Continuation

            ______________<--- Change of Structure (CoCh)
           /\                   (Reversal Level)
          /  \  /\
         /    \/  \
   \    / Market   \
    \  / Structure  \
     \/______________\
                      \<--- Break of Structure (BOS)
                       \        (Breakout level)

.. code-block:: python

   Reversal to Downtrend

                    /\-> Uptrend
    _______________/__\___ <-- BOS
    /\ MARKET     /    \
   /  \STRUCTURE /      \  /\
  /    \  /\    /        \/  \
        \/  \  /              \
             \/________________\__ <-- CoCh (Breakdown)
                                \
                                 \ <-- Reversal to downtrend

.. code-block:: python

   Reversal to Uptrend

                                   /<-- Reversal to uptrend
          ________________________/__
         /\                      /   <-- CoCh (Breakout)
        /  \  /\                /
       /    \/  \          /\  /
 \    / Market   \        /  \/
  \  / Structure  \      /
   \/______________\___ /___ <-- BOS
                    \  /
                     \/ <-- Downtrend


.. toctree::

   usage
   swing_algorithm
