#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 19-06-2023 11:24:29
# 
# file          | scripts/syncGithub.py
# project       | repdeb-helferling
# file version  | 1.0
#
from scripts.logging import logging
from scripts.configHandler import configInteractor

import subprocess
import traceback
import wget
import os


class githubInteractor():
    
    # look for latest release on github
    def getLatestRelease(self, repository):
        try:
            fullRepositoryName = configInteractor.getFullRepositoryName(self, repository)
        except:
            logging.writeError(self, "Failed to get full repository name from file - check your config at " + repository + " 'repo_name'")
            logging.writeExecError(self, traceback.format_exc())
            return
    
        try: 
            getLatestVersionCommand = "curl https://api.github.com/repos/" + fullRepositoryName + "/releases/latest -s | grep 'tag_name' | awk '{print substr($2, 2, length($2)-3) }'"
            latestVersionEncoded = subprocess.run(getLatestVersionCommand, capture_output=True, shell=True)
            # decode and remove last \n 
            latestVersion = latestVersionEncoded.stdout.decode()[:-1]
            if not latestVersion: 
                logging.writeError(self, "Was not able to retrieve latest version for " + repository)
                return False
            return latestVersion
        
        except:
            logging.writeError(self, "Failed to get full repository name from file - check your config at " + repository + " 'repo_name'")
            logging.writeExecError(self, traceback.format_exc())
            return False

    # remove unwanted letters from version
    def editVersion(self, version):
        if "-" in version:
            logging.writeDebug(self, "Editing of version required: " + version)
            return version.rsplit("-", 1)[0]
        return version

    # edit name of file / add architecture if not in
    def renameFile(self, file, architecture):
        try:
            if not architecture in file:
                fileNameNew = file.replace(".deb", "_" + architecture + ".deb")
                logging.writeDebug(self, "New filename for downloaded file " + str(file) + " is " + str(fileNameNew))
                fileNameNewPath = self.downloads + file, self.downloads + fileNameNew
                logging.writeDebug(self, "New filepath is " + str(fileNameNewPath))
                os.rename(fileNameNewPath[0], fileNameNewPath[1])
        except:
            logging.writeError(self, "Failed to move all downloads to repository's directory")
            logging.writeExecError(self, traceback.format_exc())

    # update downloaded version in ini file
    def updateVersion(self, repository, version, oldversion):
        logging.write(self, "Updating version in config for " + repository + " from " + oldversion + " to " + version)
        self.cnfgImp[repository.upper()]["version"] = version
        logging.writeDebug(self, "New local version of " + repository + " was set to " + self.cnfgImp[repository.upper()]["version"])

    # download latest release files
    def downloadHandler(self, repository, version, oldversion):
        
        # get architectures
        try:
            architectures = self.cnfgImp[repository.upper()]["architectures"].split(",")
            packages = self.cnfgImp[repository.upper()]["packages"].split(",")
            logging.writeDebug(self, "Got packages and architectures for " + repository + ", Packages: " + str(packages) + ", Architectures: " + str(architectures))
        except:
            logging.writeError(self, "Failed to get architectures from file - check your config at " + repository + " 'repo_name'")
            logging.writeExecError(self, traceback.format_exc())
            return False
        
        # edit version to download-compatible version, if release is 1.1.7-7 but download 1.1.7
        downloadVersion = githubInteractor.editVersion(self, version) 

        # get naming schemes from file
        for architecture in architectures:
            logging.writeDebug(self, "Syncing architecture (" + architecture + ") for " + repository)
            nameSchemeFromFile = self.cnfgImp[repository.upper()]["name_scheme_" + architecture]
            
            # iterate through packages 
            for package in packages:
                logging.writeDebug(self, "Syncing package " + package + " of " + repository)
                finalPackage = nameSchemeFromFile.replace("?PACKAGE?", package).replace("?VERSION?", downloadVersion)
                
                # download file
                urlToDownload = "https://github.com/" + self.cnfgImp[repository.upper()]["repo_name"] + "/releases/download/" + version + "/" + finalPackage
                try: 
                    wget.download(urlToDownload, self.downloads + finalPackage)
                    # print empty line 
                    print()
                    logging.write(self, "Downloaded " + finalPackage + " successfully")
                except:
                    logging.writeError(self, "Failed to download " + finalPackage)
                    logging.writeExecError(self, traceback.format_exc())
                    return
                try: githubInteractor.renameFile(self, finalPackage, architecture)
                except: 
                    logging.writeError(self, "Could not rename files")
                    logging.writeExecError(self, traceback.format_exc())
                try: githubInteractor.updateVersion(self, repository, version, oldversion)
                except: 
                    logging.writeError(self, "Could not update version in config file")
                    logging.writeExecError(self, traceback.format_exc())
