import datetime
import functools


def log_time_spent(log_message="Time spent"):
    def decorator_provider(decorated):
        @functools.wraps(decorated)
        def decorator(*args, **kwargs):
            start_time = datetime.datetime.now()
            print "\t[Starting {}]".format(decorated.__name__)
            return_value = decorated(*args, **kwargs)
            end_time = datetime.datetime.now()
            seconds_spent = (end_time - start_time).seconds
            print "\t[Time spent in {}]: {} seconds".format(decorated.__name__, seconds_spent)
            return return_value
        return decorator
    return decorator_provider
