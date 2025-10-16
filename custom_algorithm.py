# Custom algorithm: Find 5 longest trips without using built-in sort
def top_longest(trips):
    top = [None]*5
    for trip in trips:
        duration = trip['trip_duration']
        for i in range(5):
            if top[i] is None or duration > top[i]['trip_duration']:
                top.insert(i, trip)
                top.pop()
                break
    return top

# O(n * k) time, O(k) space
