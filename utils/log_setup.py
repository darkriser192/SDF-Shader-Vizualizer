"""
My personal loger implementation

# TODO: Need to implement multiple levels and writing to a file

"""
import logging

def setup_logger(Name="Default_Logger_Name", level=logging.DEBUG):
    logger = logging.getLogger(Name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s", "%H:%M:%S")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger