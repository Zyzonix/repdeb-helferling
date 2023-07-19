#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 08-06-2023 13:04:10
# 
# file          | repdeb-helferling/repdeb-sync.py
# project       | repdeb-helferling
# project-v     | 2.0
# file version  | 2.0
#

#
# Description: source deb packges from github releases
# -> run this daily to be always up to date (via crontab) see README
#

# import other scripts
from scripts.logging import logging 
from scripts.configHandler import configInteractor 
from scripts.syncGithub import githubInteractor
from scripts.fileHandler import fileHandler

from configparser import ConfigParser
import traceback

# static config
# basepath = path to directory repdeb-helferling
basepath = "/root/repdeb-helferling/"
configFile = "repdeb-sync-config.ini"
configFileGeneral = "GENERAL"

class core():

    # main process handler
    def runner(self):

        packagesFilenameSet = {}
        verifySuccessful = False
        fileMoveSuccessful = False

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
            
            releaseData = githubInteractor.getReleaseAsJSON(self, repository)
            if releaseData:

                # extract latest release
                logging.writeDebug(self, "Got release JSON for "+ repository)
                latestRelease = releaseData["tag_name"]
                logging.writeDebug(self, "Latest release for " + repository + " is " + latestRelease)

                # check if remote latest version is locally available
                localCurrentRelease = configInteractor.getCurrentReleaseFromFile(self, repository)
                logging.writeDebug(self, "Local version of " + repository + " is " + localCurrentRelease + ", remote is " + latestRelease)
                
                # if local and remote version are equal -> lookup next
                if not localCurrentRelease == latestRelease:
                    logging.write(self, "Update available for " + repository + " " + localCurrentRelease + " -> " + latestRelease)
                    if not ("beta" or "alpha") in latestRelease: 
                        logging.writeDebug(self, "Release for " + repository + " is not alpha/beta")

                        # append package name to list to indicate which downloads were successful
                        packagesFilenameSet.update(githubInteractor.downloadHandler(self, repository, releaseData, latestRelease, localCurrentRelease))
                        
                    else:
                        logging.write(self, repository + "'s latest release contains alpha/beta - skipping")
                
                # if version is the latest
                else:
                    logging.write(self, "Local version is the newest - skipping " + repository)
                    logging.writeDebug(self, "Local version: " + localCurrentRelease + " - Latest version on GitHub: " + latestRelease)

            else:
                logging.writeError(self, "Wasn't able to get release data for " + repository + " - skipping")

        # finally move all files and update versions in config
        if packagesFilenameSet: fileMoveSuccessful = fileHandler.moveFiles(self)

        # verify filenames in index.ini, filesNotInIndex unused
        if self.autocleanup: verifySuccessful, filesToRemoveFromIndex, filesNotInIndex = fileHandler.verifyIndex(self, packagesFilenameSet)
        if verifySuccessful and fileMoveSuccessful: 
            logging.write(self, "Moving and verifying files successful")  

            # remove old binaries/packages
            # filesToRemoveFromIndex contains old packages as dict: package: [filelist]
            if packagesFilenameSet and filesToRemoveFromIndex: fileHandler.cleanUp(self, filesToRemoveFromIndex)
       
        # updated main config file
        configInteractor.updateConfig(self)
        logging.write(self, "Finished syncing. Exiting...")
        logging.write(self, "")


    def __init__(self):

        # create config importer
        self.cnfgImp = ConfigParser(comment_prefixes='/', allow_no_value=True)
        
        # open config.ini file
        self.cnfgImp.read(basepath + configFile)

        try:
            # get logfile path
            self.logFileDir = self.cnfgImp[configFileGeneral]["logfiledir"]
            self.downloads = self.cnfgImp[configFileGeneral]["downloads"]
            self.finalDebDir = self.cnfgImp[configFileGeneral]["final_deb_dir"]
            self.loglevel = int(self.cnfgImp[configFileGeneral]["loglevel"])
            self.autocleanup = self.cnfgImp.getboolean("GENERAL", "autocleanup")
            # make basepath accessible everywhere
            self.basepath = basepath

            # import static variables as self variable
            self.configFileGeneral = configFileGeneral
            self.configFile = configFile
            logging.write(self, "-----------------------")
            logging.write(self, "| Running REPDEB-SYNC |")
            logging.write(self, "-----------------------")
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
