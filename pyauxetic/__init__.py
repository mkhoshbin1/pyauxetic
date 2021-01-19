

from .version import __version__


import logging
#import classes

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
debug_handler = logging.FileHandler(filename='log_debug.log', mode='w')
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(logging.Formatter(
    '%(asctime)s -%(levelname) 7s - %(module)s.%(funcName)s - %(message)s' ) )
info_handler  = logging.FileHandler(filename='log.log', mode='w')
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname) 5s - %(message)s' ) )
logger.addHandler(debug_handler)
logger.addHandler(info_handler)


#TODO: why does one of the logs show in reentrant's __init__?