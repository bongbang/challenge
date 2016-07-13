# Insight coding challenge submission

This program (`src/venmo_degree.py`) calculates the rolling median degree of nodes representing users of the Venmo payment service within a 60-second window of the latest transaction. For the `run.sh` demonstration, the input is `venmo_input/venmo-trans.txt` and the output, `venmo_output/output.txt`.

## Requirements

**Python 3.5** or later is required for the [deque][] object's `insert` method. The program checks for this requirement on startup and will not proceed further if it is not met. There are no other requirements.

[deque]: https://docs.python.org/3/library/collections.html#collections.deque

## Design

I aim for the sweet spot between performance and memory-efficiency. Without rigorous benchmarking, I estimate that every step of the program is carried out in roughly constant time (*O(1)*), with a modest memory requirement. The largely repetitive degrees are efficiently stored in a frequency table (implemented as a humble list), which yields automatic sorting. Memory footprint is further reduced by storing edges as sorted `tuples` instead of `frozensets`.

Only a transaction with a valid payor, payee, and timestamp is processed. The payor and the payee cannot be the same person in a transaction.
