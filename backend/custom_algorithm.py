"""
Custom algorithms for the assignment's requirement to implement at least one
algorithm/data structure without built-ins.

Includes:
- Fixed-size Top-K by duration (insertion into a small buffer)
- Simple streaming anomaly detector using rolling mean/variance (Welford)
"""


def top_k_longest_by_duration(trips, k=5):
    """Maintain a fixed-size buffer of top-k trips by trip_duration.

    Runs in O(n * k) time, O(k) space. Avoids using sort or heap.
    """
    top = [None] * k
    for trip in trips:
        duration = trip['trip_duration']
        for i in range(k):
            if top[i] is None or duration > top[i]['trip_duration']:
                top.insert(i, trip)
                top.pop()  # keep size at k
                break
    return [t for t in top if t is not None]


def streaming_anomaly_flags(values, m=3.0):
    """Yield booleans indicating m-sigma anomalies using Welford's algorithm.

    - values: iterable of numbers
    - m: threshold in standard deviations for anomaly
    Yields: (index, value, is_anomaly)
    """
    count = 0
    mean = 0.0
    m2 = 0.0  # sum of squares of differences from the current mean
    for idx, x in enumerate(values):
        count += 1
        delta = x - mean
        mean += delta / count
        delta2 = x - mean
        m2 += delta * delta2

        if count < 2:
            yield (idx, x, False)
            continue

        variance = m2 / (count - 1)
        std = variance ** 0.5
        is_anom = std > 0 and (abs(x - mean) > m * std)
        yield (idx, x, is_anom)
