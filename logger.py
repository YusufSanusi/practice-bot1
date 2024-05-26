# encoding: utf-8

import logging as log
import os
from datetime import datetime

def initialize_logger():
    # today's date
    today = datetime.now()

    # create a folder for the logs
    logs_path = './logs/'
    try:
        os.mkdir(logs_path)
    except Exception as e:
        if "file already exists" not in str(e):
            log.error(str(e))
            # log.error(str(OSError))
            print("Creation of the directory %s failed - it does not mean doom and gloom" % logs_path)
    else:
        print("Successfully created log directory")

    #renaming each log depending on the time

    log_name = logs_path + today.strftime("%Y%m%d_%H") + '.log'

    # configuring logger
    log.basicConfig(filename=log_name, format='%(asctime)s - %(levelname)s: %(message)s', level=log.DEBUG)
    log.getLogger().addHandler(log.StreamHandler())

    # logging levels: DEBUG, INFO, WARNING, ERROR

    # log initialized message
    log.info('Log initialized')
