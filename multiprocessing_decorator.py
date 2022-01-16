from multiprocessing import Process

result_dict = []

def multiprocessing_decorator(func):
    def wrapper_multiprocessing_decorator(*args, **kwargs):
        p = Process(target=func, args=args, kwargs=kwargs)
        p.start()
        p.join()

    return wrapper_multiprocessing_decorator
