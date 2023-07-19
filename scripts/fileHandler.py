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
# file version  | 2.0
#
from scripts.logging import logging
from scripts.configHandler import configInteractor
from scripts.configHandler import indexInteractor
from scripts.syncGithub import architecture_alias_list

import os
import shutil
import traceback
import subprocess


class fileHandler():

    # check/validate architecture of DEB file 
    def checkArchitecture(self, file):
        if not ".deb" in file:
            logging.writeError(self, "File is not a .deb package")
            return False
        else:
            package_architecture_raw = subprocess.run("/usr/bin/dpkg --info " + file + " | grep Architecture", capture_output=True, shell=True)
            package_architecture = str(package_architecture_raw.stdout.decode()[:-1])
            logging.writeDebug(self, "Architecture for '" + file + "' is '" + package_architecture + "'")
            
            # move all packages for "all" to amd64 directory
            if "all" in package_architecture: return "amd64"

            # get directory for package
            for architecture in architecture_alias_list.keys():
                if architecture in package_architecture: 
                    logging.writeDebug(self, file + " has architecture '" + architecture + "'")
                    return architecture


    # move all files to correct dir
    def moveFiles(self):
        filesToMove = os.listdir(self.downloads)
        if filesToMove: logging.write(self, "Moving downloaded files to final repository directory (" + self.finalDebDir + ")")
        if not self.downloads in self.finalDebDir:
            logging.writeDebug(self, "Final and download directory are different: "  + self.downloads + " and " + self.finalDebDir)
            try: 
                final_architecture_directories = configInteractor.getFinalDirs(self)
                for file in filesToMove:
                    downloadedFile = self.downloads + file
                    file_architecture = fileHandler.checkArchitecture(self, downloadedFile)
                    logging.writeDebug(self, "Architecture of " + str(file) + " is " + str(file_architecture))
                    targetLocationDownloadFile = self.finalDebDir + final_architecture_directories[file_architecture] + file
                    logging.writeDebug(self, "Downloaded file: " + downloadedFile)
                    logging.writeDebug(self, "Target file location: " + targetLocationDownloadFile)
                    shutil.move(downloadedFile, targetLocationDownloadFile)
            except:
                logging.writeError(self, "Failed to move all downloads to repository's directory")
                logging.writeExecError(self, traceback.format_exc())
                return False
            return True
        else:
            logging.writeDebug(self, "Final directory is part of download directory - moving not possible")

    # get all binary directories and files in it
    def getDirectories(self):
        final_directories = []
        
        final_architecture_directories = configInteractor.getFinalDirs(self)
        final_directory_base = self.finalDebDir

        # merge paths
        for directory_key in final_architecture_directories.keys():
            final_directories.append(final_directory_base + final_architecture_directories[directory_key])
        
        return final_directories

    # get all files in directories, returns array
    def getFiles(self, directoryList):
        fileList = {}

        for directory in directoryList:
            fileList[directory] = os.listdir(directory)

        logging.writeDebug(self, "File list: " + str(fileList))
        return fileList

    # verify filenames under static/index.ini, returns two lists:
    # filesToRemoveFromIndex (files that should be removed, because a newer version was downloaded), 
    # filesNotInIndex (unused, files that were found but not registered in index)
    def verifyIndex(self, packagesFilenameSet):
        
        # if no updated were made set packagesFilenameSet to empty dict to prevent errors, functions will then be skipped
        if not packagesFilenameSet: packagesFilenameSet = {}
 
        indexHandler = indexInteractor.getIndexHandler(self)

        final_directories = fileHandler.getDirectories(self)
        # fileList is dict with directory:[file1,file2]
        fileList = fileHandler.getFiles(self, final_directories)
        filesInIndex = []
        toNewIndex = {}
        filesToRemoveFromIndex = {}
        # packages (only keys in dicts) that were updated, to rewrite index
        asUpdatedMarkedPackages = []
        # contains files that aren't listed in index
        filesNotInIndex = []

        # get all entries from index
        if indexHandler:
            try: 
                # get files from file
                packagesIndexDict = dict(indexHandler.items("FILES"))
                for package in packagesIndexDict.keys():
                    for file in indexHandler["FILES"][package].split(","):
                        filesInIndex.append(file)

                    # check which packages were updated, fileName = exact .deb file name
                    # if value (package name) of key (filename) is in newly downloaded file set, mark it --> remove
                    if package in packagesFilenameSet.keys():
                        asUpdatedMarkedPackages.append(package)
                        # collect files to remove
                        filesToRemoveFromIndex[package] = indexHandler["FILES"][package].split(",")
                    
                logging.writeDebug(self, "Verify - got packages from old index file: " + str(filesInIndex))
                logging.writeDebug(self, "Verify - updated packages: " + str(asUpdatedMarkedPackages))

                # add all newly downloaded files to toNewIndex variable
                for package in packagesFilenameSet.keys():
                    # initialize 
                    toNewIndex[package] = ""
                    for file in packagesFilenameSet[package].keys():
                        toNewIndex[package] += file + ","

                    # remove last ','  
                    toNewIndex[package] = toNewIndex[package][:-1]

                logging.writeDebug(self, "Verify - adding all newly downloaded files to new index file: " + str(toNewIndex))
                logging.writeDebug(self, "Verfiy - files to remove: " + str(filesToRemoveFromIndex))
 
                for directory in fileList.keys():
                    logging.writeDebug(self, "Verify - checking directory for unregistered files: " + directory)
                    for file in fileList[directory]:
                        if not file in filesInIndex:
                            logging.writeDebug(self, "Verify - unregistered file found: " + file)
                            filesNotInIndex.append(file)
                
                # update index
                for updatedPackage in toNewIndex.keys():
                    indexHandler["FILES"][updatedPackage] = toNewIndex[updatedPackage]
                
                writeIndexSuccessful = indexInteractor.writeIndex(self, indexHandler)
                if writeIndexSuccessful: logging.write(self, "Verify - new files indexed")
                
                return True, filesToRemoveFromIndex, filesNotInIndex
            except:
                logging.writeError(self, "Failed to index directories")
                logging.writeExecError(self, traceback.print_exc())
                return False, filesToRemoveFromIndex, filesNotInIndex
        else:
            logging.writeError(self, "IndexHandler not accessible")
            return False, filesToRemoveFromIndex, filesNotInIndex

        
    # cleanup old binaries / packages after moving new packages to directory
    def cleanUp(self, filesToRemoveFromIndex):
        logging.write(self, "Starting final dir cleanup")
        backupDirectory = configInteractor.getBackupDirectory(self)
        final_directories = fileHandler.getDirectories(self)

        # backup all directories
        if backupDirectory:
            for directory in final_directories:
                for file in os.listdir(directory):
                    shutil.copy(directory + file, self.basepath + backupDirectory + file)

        # current packages in directories
        if final_directories:
            logging.writeDebug(self, "final_directories: " + str(final_directories))

            fileList = fileHandler.getFiles(self, final_directories)

            for final_directory in fileList.keys():
                logging.writeDebug(self, "Selected directory: " + final_directory)
                for package in filesToRemoveFromIndex.keys():
                    for file in filesToRemoveFromIndex[package]:
                        if file in fileList[final_directory]:
                            try:
                                os.remove(final_directory + file)
                                logging.writeDebug(self, "Deleted " + final_directory + file)
                            except:
                                logging.writeError(self, "Failed to remove " + final_directory + file)
                                logging.writeExecError(self, traceback.print_exc())

            return True
        else:
            logging.writeError(self, "No final directory, can't cleanup old binaries")
            return False