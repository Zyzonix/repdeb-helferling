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
# file version  | 2.0
#

from scripts.logging import logging
from scripts.time import time

import traceback
from configparser import ConfigParser

class indexInteractor():

    # write index to file
    def writeIndex(self, indexHandler):
        try: 
            indexFileChange = open(self.basepath + "static/index.ini", "w")
            indexHandler.write(indexFileChange)
            return True
        except: 
            logging.writeError(self, "Failed to write index to file")
            logging.writeExecError(self, traceback.print_exc())
            return False

    # get index handler
    def getIndexHandler(self):
        indexHandler = ConfigParser(comment_prefixes='/', allow_no_value=True)
        try:
            indexHandler.read(self.basepath + "static/index.ini")
            logging.writeDebug(self, "Reading of index file successful")
            return indexHandler
        except:
            logging.writeError(self, "Verifying - Was not able to open static/index.ini file")
            logging.writeExecError(self, traceback.print_exc())
            return False


class configInteractor():

    # get final deb dirs for architectures
    def getFinalDirs(self):
        final_architecture_directories = {}
        try:
            final_architecture_directories["amd64"] = self.cnfgImp[self.configFileGeneral]["final_dir_amd64"]
            final_architecture_directories["arm64"] = self.cnfgImp[self.configFileGeneral]["final_dir_arm64"]
            final_architecture_directories["armhf"] = self.cnfgImp[self.configFileGeneral]["final_dir_armhf"]
            logging.writeDebug(self, "Final directories are " + str(final_architecture_directories))
            return final_architecture_directories
        except:
            logging.writeExecError(self, traceback.print_exc())
            logging.writeError(self, "Failed to get final dirs for architectures using default dir for all")
            return False

    # update downloaded version in ini file
    def updateVersion(self, repository, version, oldversion):
        logging.write(self, "Updating version in config for " + repository + " from " + oldversion + " to " + version)
        self.cnfgImp[repository.upper()]["version"] = version
        logging.writeDebug(self, "New local version of " + repository + " was set to " + self.cnfgImp[repository.upper()]["version"])

    # get packages to download (if there are more than one)
    def getPackages(self, repository):
        try:
            packages = self.cnfgImp[repository.upper()]["packages"].split(",")
            logging.writeDebug(self, "Got packages for " + repository)
            return packages
        except:
            logging.writeError(self, "Failed to get packages from file - check your config at " + repository + ": 'repo_name'/'packages'")
            logging.writeExecError(self, traceback.format_exc())
            return False

    # get default setting if all architectures should be synced
    def resolveAllArchitectures(self):
        try:
            architectures = self.cnfgImp[self.configFileGeneral]["all_architectures"].split(",")
            logging.writeDebug(self, "Default architectures are " + str(architectures))
            return architectures
        except:
            logging.writeExecError(self, traceback.print_exc())
            logging.writeError(self, "Was not able to import all_architectures from config - using now 'arm64,amd64'")
            return ["arm64", "amd64"]

    # get architectures to download
    def getArchitectures(self, repository):
        try:
            architectures = self.cnfgImp[repository.upper()]["architectures"].split(",")
            logging.writeDebug(self, "Got architectures for " + repository + " = " + str(architectures))
            return architectures
        except:
            logging.writeError(self, "Failed to get architectures from file - check your config at " + repository + ": 'repo_name'/'architectures'")
            logging.writeExecError(self, traceback.format_exc())
            return False

    # get directory for backups
    def getBackupDirectory(self):
        try: 
            backup_enabled = self.cnfgImp.getboolean(self.configFileGeneral, "backup")
            backupDirectory = self.cnfgImp[self.configFileGeneral]["backupdirectory"]
            if backup_enabled: 
                logging.writeDebug(self, "Backup enabled")
                return backupDirectory
            else: return False
        except:
            logging.writeError(self, "Failed to get backup directory")
            logging.writeExecError(traceback.print_exc())
            return False

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
            configFileChange = open(self.basepath + self.configFile, "w")
            self.cnfgImp.write(configFileChange)
            logging.writeDebug(self, "Updated config file successfully")
        except:
            logging.writeError(self, "Updating config file failed")
            logging.writeExecError(self, traceback.format_exc())
            return False