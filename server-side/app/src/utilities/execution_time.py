from functools import wraps
from time import time as timer


def execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'------{func.__name__}------')
        start_time = timer()
        result = func(*args, **kwargs)
        end_time = timer()
        execution_time = end_time - start_time
        print(f"{func.__name__} took {execution_time:.5f} seconds!")
        print(f'------------------------------')
        return result
    return wrapper
