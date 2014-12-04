#! python
import logging
from logging.handlers import RotatingFileHandler
import os

def initRotatingLogger(logName, fileName, logDir=None, toScreen=True, toText=True, logLevel=logging.WARNING):

    if not os.path.exists(logDir): os.makedirs(os.path.abspath(logDir))

    logger = logging.getLogger(logName)
    logger.setLevel(logLevel)

    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s :: %(message)s")

    if toText:
        txt_handler = RotatingFileHandler(os.path.join(logDir, fileName), backupCount=5)
        txt_handler.doRollover()
        txt_handler.setFormatter(log_formatter)
        logger.addHandler(txt_handler)
        logger.info("Logger initialized.")

    if toScreen:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)
        
    return logger