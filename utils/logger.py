import logging


def init_logger():
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger()
    logger_handler = logging.StreamHandler()
    logger.addHandler(logger_handler)
    logger.removeHandler(logger.handlers[0])

    formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s: %(message)s")
    logger_handler.setFormatter(formatter)