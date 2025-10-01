import random
import time
from statistics import mean

from API.datastore import load_default_store


def time_call(fn, *args, **kwargs):
    repeats = kwargs.pop("repeats", 1000)
    durations = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn(*args, **kwargs)
        durations.append(time.perf_counter() - start)
    return mean(durations)


def main():
    store = load_default_store()

    if len(store.transactions) < 20:
        needed = 20 - len(store.transactions)
        for _ in range(needed):
            store.create_transaction({
                "transaction_type": "test",
                "amount": random.uniform(1, 100),
                "sender": "A",
                "receiver": "B",
                "timestamp": str(time.time()),
            })

    sample_ids = [tx["id"] for tx in store.transactions[:20]]

    linear_times = []
    dict_times = []
    for tx_id in sample_ids:
        linear_t = time_call(store.linear_search_by_id, tx_id, repeats=500)
        dict_t = time_call(store.dict_lookup_by_id, tx_id, repeats=500)
        linear_times.append(linear_t)
        dict_times.append(dict_t)

    print("Records compared:", len(sample_ids))
    print("Linear search avg time: %.2f µs" % (mean(linear_times) * 1e6))
    print("Dict lookup avg time:  %.2f µs" % (mean(dict_times) * 1e6))
    print("Observation: Dictionary lookup is usually O(1) average, linear is O(n).")


if __name__ == "__main__":
    main()
