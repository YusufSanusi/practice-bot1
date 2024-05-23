#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging as lg
import os
from datetime import datetime

# today's date
today = datetime.now()

# create a folder for the logs
logs_path = './logs/'
try:
    os.mkdir(logs_path)
except OSError:
    print("Creation of the directory %s failed - it does not mean doom and gloom" % logs_path)
else:
    print("Successfully created log directory")

#renaming each log depending on the time

log_name = logs_path + today.strftime("%Y%m%d_%H") + '.log'

# configuring logger

lg.basicConfig(filename=log_name, format='%(asctime)s - %(levelname)s: %(message)s', level=lg.DEBUG)
lg.getLogger().addHandler(lg.StreamHandler())

# logging levels: DEBUG, INFO, WARNING, ERROR

lg.info('This is an info message!')
lg.error('This is an error message!')
