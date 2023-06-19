#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 08-06-2023 13:04:10
# 
# file          | repo-helper/sync-repo-from-github.py
# project       | repo-helper
# project-v     | 1.1
# file version  | 1.1
#

#
# Description: source deb packges from github releases
# -> run this daily to be always up to date (via crontab)
#

# import other scripts
from scripts.logging import logging 
from scripts.configHandler import configInteractor 
from scripts.syncGithub import githubInteractor
from scripts.fileHandler import fileHandler


from datetime import datetime
from configparser import ConfigParser
import os
import traceback
import shutil

# static config
configFile = "repdeb-sync-config.ini"
# configFile = "/root/repdeb-helferling/repdeb-sync-config.ini"
configFileGeneral = "GENERAL"

class core():

    # main process handler
    def runner(self):

        # try importing repos from file
        try:
            repositoriesToSync = configInteractor.getRepositories(self)
            logging.writeDebug(self, "Got all repositories to sync: " + str(repositoriesToSync))
        except:
            logging.writeError(self, "Failed to import repositories to sync from file")
            logging.writeExecError(self, traceback.format_exc())
            return
        
        for repository in repositoriesToSync:
            logging.write(self, "Trying to sync " + repository)
            
            # get latest release
            lastestRelease = githubInteractor.getLatestRelease(self, repository)
            logging.writeDebug(self, "Latest release for " + repository + " is " + lastestRelease)
            
            # check if remote latest version is locally available
            localCurrentRelease = configInteractor.getCurrentReleaseFromFile(self, repository)
            logging.writeDebug(self, "Current local version of " + repository + " is " + localCurrentRelease)

            # if local and remote version are equal -> lookup next
            if not localCurrentRelease == lastestRelease:
                logging.writeDebug(self, "Local version of " + repository + " is different than on Github")
                
                if not ("beta" or "alpha") in lastestRelease: 
                    logging.write(self, "Update available for " + repository)
                    githubInteractor.downloadHandler(self, repository, lastestRelease, localCurrentRelease)
                else:
                    logging.write(self, repository + "'s latest release contains alpha/beta - skipping")
            
            # if version is the latest
            else:
                logging.write(self, "Local version is the newest - skipping " + repository)
                logging.writeDebug(self, "Local version: " + localCurrentRelease + " - Latest version on GitHub: " + lastestRelease)
                
        # finally move all files and update versions in config
        fileHandler.fileHandler(self)
        configInteractor.updateConfig(self)
            

    def __init__(self):

        # create config importer
        self.cnfgImp = ConfigParser(comment_prefixes='/', allow_no_value=True)
        
        # open config.ini file
        self.cnfgImp.read(configFile)

        try:
            # get logfile path
            self.logFileDir = self.cnfgImp[configFileGeneral]["logfiledir"]
            self.downloads = self.cnfgImp[configFileGeneral]["downloads"]
            self.finalDebDir = self.cnfgImp[configFileGeneral]["final_deb_dir"]
            self.loglevel = int(self.cnfgImp[configFileGeneral]["loglevel"])

            # import static variables as self variable
            self.configFileGeneral = configFileGeneral
            self.configFile = configFile
            logging.writeDebug(self, "Got all variables, logFileDir: " + self.logFileDir + ", downloads: " + self.downloads + ", finalDebDir: " + self.finalDebDir + ", configFile: " + self.configFile)
        except:
            print(traceback.format_exc())
            print("ERROR  | Wasn't able to read config file")
            print("ERROR  | Check your if the path to your config.ini in core.py is correct!")
            return
        
        # start main function
        logging.writeDebug(self, "Starting runner (core function)")
        self.runner()


if __name__ == "__main__":
    core() 
