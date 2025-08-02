import time
from itertools import repeat
from functools import wraps


def repeat_func(count_call):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not isinstance(count_call, int) or count_call <= 0:
                raise ValueError(f"`count_call` must be a positive integer, got: {count_call}")

            start_time = time.perf_counter()

            results = [func(*args, **kwargs) for _ in repeat(None, count_call)]

            end_time = time.perf_counter()

            total_time = (end_time - start_time)
            avg_time = total_time / count_call

            print(f"Total calls: {count_call}")
            print(f"Total time: {total_time:.6f} seconds")
            print(f"Average time per call: {avg_time:.6f} seconds")

            return results if count_call > 1 else results[0]

        return wrapper

    return decorator


@repeat_func(count_call=5)
def sum_elem(a: int, c: int) -> int:
    return a + c


if __name__ == "__main__":
    print(sum_elem(2, 6))
