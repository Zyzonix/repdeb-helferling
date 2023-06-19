#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 19-06-2023 11:59:41
# 
# file          | scripts/time.py
# project       | repdeb-helferling
# file version  | 1.0.0
#

from datetime import datetime

# time for logging / console out
class time():
    def getTime():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        return curTime