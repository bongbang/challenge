# Insight coding challenge submission

This program (`src/venmo_degree.py`) calculates the rolling median degree of nodes representing users of the Venmo payment service within the 60-window of the latest transaction. For the `run.sh` demonstration, the input is `venmo_input/venmo-trans.txt` and the output, `venmo_output/output.txt`.

# Requirements

**Python 3.5** or later is required for the [deque][] object's `insert` method. The program checks for this requirement on startup and will not proceed further if it is not met. There are no other requirements.

[deque]: https://docs.python.org/3/library/collections.html#collections.deque

# Design

I aim for a sweet spot between performance and memory-economy. Without rigorous benchmarking, I estimate that every step of program is carried out in constant time (O(1)), with a modest memory footprint. The degrees are efficiently stored in a frequency table (implemented with a humble list), which yields automatic sorting. Memory requirement is further reduced by storing edges as sorted `tuples` instead of `frozensets`.

Only a transaction with a valid payer, payee, and time is processed. The payee and the payee cannot be the person in a given transaction.
