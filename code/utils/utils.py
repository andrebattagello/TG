import datetime
import functools

def log_time_spent(log_message="Time spent"):
    def decorator_provider(decorated):
        @functools.wraps(decorated)
        def decorator(*args, **kwargs):
            start_time = datetime.datetime.now()
            print "\n\t[Starting {}]".format(decorated.__name__)
            return_value = decorated(*args, **kwargs)
            end_time = datetime.datetime.now()
            print "\n\t[Time spent in {}]:".format(decorated.__name__), (end_time - start_time).seconds, "seconds"
            return return_value
        return decorator
    return decorator_provider
