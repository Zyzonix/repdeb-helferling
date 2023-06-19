#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 19-06-2023 11:15:39
# 
# file          | scripts/logging.py
# project       | repdeb-helferling
# file version  | 1.0
#
from scripts.time import time

from datetime import datetime
import os

class logging():
    # delete old logfiles, only keep last month
    def logFileCleanUp(self):
        for file in os.listdir(self.logFileDir):
            filename = file.split(".")[0]
            fileNameContents = filename.split("-")
            if (int(fileNameContents[0]) < int(datetime.now().strftime("%Y"))) or (int(fileNameContents[1]) < (int(datetime.now().strftime("%m")) - 1)):
                logging.writeDebug(self, "Found old log file: " + self.logFileDir + file)
                os.remove(self.logFileDir + file)
                logging.writeDebug(self, "Deleted old log file(s)")

    def toFile(self, msg):
        if not (os.path.isdir(self.logFileDir)): os.system("mkdir -p " + self.logFileDir)
        logFile = open(self.logFileDir + str(datetime.now().strftime("%Y-%m")) + ".log", "a")
        logFile.write(msg + "\n")
        logFile.close()
        logging.logFileCleanUp(self)

    def write(self, msg):
        message = str(time.getTime() + " INFO   | " + str(msg))
        print(message)
        logging.toFile(self, message)

    def writeError(self, msg):
        message = str(time.getTime() + " ERROR  | " + msg)
        print(message)
        logging.toFile(self, message)

    # log/print error stack trace
    def writeExecError(self, msg):
        message = str(msg)
        print(message)
        logging.toFile(self, message)

    def writeDebug(self, msg):
        # check if loglevel is debug (1=INFO,2=DEBUG)
        if self.loglevel == 2:
            message = str(time.getTime() + " DEBUG  | " + msg)
            print(message)
            logging.toFile(self, message)

    def writeSubprocessout(self, msg):
        for line in msg:
            line = str(line)
            line = line[:-3]
            line = line[3:]
            logging.write(self, "SYS   | " + line)
