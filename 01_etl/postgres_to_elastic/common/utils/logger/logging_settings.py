LOGGER_SETTINGS = {
    "format": "%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",  # noqa 501
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "level": logging.INFO,
    "handlers": [logging.StreamHandler()],
}