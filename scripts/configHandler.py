#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 19-06-2023 11:15:12
# 
# file          | scripts/configHandler.py
# project       | repdeb-helferling
# file version  | 1.0
#

from scripts.logging import logging
from scripts.time import time
import traceback

class configInteractor():

    # get current downloaded version from config
    def getCurrentReleaseFromFile(self, repository):
        try:
            currentRelease = self.cnfgImp[repository.upper()]["version"]
        except:
            logging.writeError(self, "Failed to get current version for " + repository + " - check 'version' in your config")
            logging.writeExecError(self, traceback.format_exc())
            return
        return currentRelease

    # get full repository name from config
    def getFullRepositoryName(self, repository):
        fullRepositoryName = self.cnfgImp[repository.upper()]["repo_name"]
        logging.writeDebug(self, "Got repository name: " + repository + " is " + fullRepositoryName)
        return fullRepositoryName

    # get repositories from file and split them to list
    def getRepositories(self):
        repositoriesFromFile = self.cnfgImp[self.configFileGeneral]["remote_sources"]
        repositoriesFromFileSplit = []

        try:
            repositoriesFromFileSplit = repositoriesFromFile.split(",")
        except:
            logging.writeError(self, "Failed to split imported repositories")
            logging.writeExecError(self, traceback.format_exc())
            return
        
        return repositoriesFromFileSplit
    
    # finally update ini file
    def updateConfig(self):
        logging.write(self, "Updating config file")
        self.cnfgImp[self.configFileGeneral]["last_update"] = str(time.getTime())
        try:
            configFileChange = open(self.configFile, "w")
            self.cnfgImp.write(configFileChange)
            logging.writeDebug(self, "Updated config file successfully")
        except:
            logging.writeError(self, "Updating config file failed")
            logging.writeExecError(self, traceback.format_exc())
            return False