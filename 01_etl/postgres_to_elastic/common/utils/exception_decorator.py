import logging

logger = logging.getLogger(__name__)


def exception_decorator(func):
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as err:
            logger.error(f'{func.__name__} {err}')
    return inner_function
