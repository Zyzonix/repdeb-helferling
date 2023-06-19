#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 19-06-2023 12:59:59
# 
# file          | scripts/fileHandler.py
# project       | repdeb-helferling
# file version  | 1.0
#
from scripts.logging import logging

import os
import shutil
import traceback


class fileHandler():

    # move all files to correct dir
    def fileHandler(self):
        filesToMove = os.listdir(self.downloads)
        if filesToMove: logging.write(self, "Moving downloaded files to final repository directory (" + self.finalDebDir + ")")
        if not self.downloads in self.finalDebDir:
            logging.writeDebug(self, "Final and download directory are different: "  + self.downloads + " and " + self.finalDebDir)
            try: 
                for file in filesToMove:
                    downloadedFile = self.downloads + file
                    targetLocationDownloadFile = self.finalDebDir + file
                    logging.writeDebug(self, "Downloaded file: " + downloadedFile)
                    logging.writeDebug(self, "Target file location: " + targetLocationDownloadFile)
                    shutil.move(downloadedFile, targetLocationDownloadFile)
            except:
                logging.writeError(self, "Failed to move all downloads to repository's directory")
                logging.writeExecError(self, traceback.format_exc())
                return False
        else:
            logging.writeDebug(self, "Final directory is part of download directory - moving not possible")
        
