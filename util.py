import inspect

def make_process(func):
    if not inspect.isgeneratorfunction(func):
        raise ValueError("Decorator @make_process must be used on a generator function")

    def make_iter_caller(it):
        called = False

        def worker():
            nonlocal called

            if called:
                raise RuntimeError("Cannot re-enter a previous point of a program")
            else:
                called = True

                try:
                    next(it)(make_iter_caller(it))
                except StopIteration:
                    pass

        return worker

    return make_iter_caller(func())
