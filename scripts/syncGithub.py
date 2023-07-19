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
# file version  | 2.0
#
from scripts.logging import logging
from scripts.configHandler import configInteractor

import traceback
import wget
import os
import json
import requests


# collect all names for architectures
# referenced in this file and fileHandler.py!
architecture_alias_list = {
    "arm64" : ["aarch64", "arm64", "armv8"],
    "amd64" : ["x86", "x86_64", "amd64"],
    "armhf" : ["arm32", "armhf", "armv7"]
}


class githubInteractor():
    
    # get full repo name user/repository from config
    def getFullRepositoryName(self, repository):
        try:   
            logging.writeDebug(self, "Trying to get fullRepositoryName of " + repository)
            fullRepositoryName = configInteractor.getFullRepositoryName(self, repository)
            logging.writeDebug(self, "Got fullRepositoryName of " + repository + " is " + fullRepositoryName)
            return fullRepositoryName
        except:
            logging.writeError(self, "Failed to get full repository name from file - check your config at " + repository + " 'repo_name'")
            logging.writeExecError(self, traceback.format_exc())
            return False

    # get latest release file from GitHub
    def getReleaseFile(self, fullRepositoryName):
        try:
            downloadedReleasePageURL = "https://api.github.com/repos/" + fullRepositoryName + "/releases/latest"
            logging.writeDebug(self, "Release file download URL for " + fullRepositoryName + " is " + downloadedReleasePageURL + " - trying to download")
            downloadedReleasePage = requests.get(downloadedReleasePageURL)
            downloadedReleasePageText = downloadedReleasePage.text
            return downloadedReleasePageText
        except:
            logging.writeError(self, "Failed to get latest release file for " + fullRepositoryName + " - skipping")
            logging.writeExecError(self, traceback.format_exc())
            return False

    # first get release page, then import to JSON variable
    def getReleaseFileJSON(self, fullRepositoryName):
        logging.writeDebug(self, "Getting release file for " + fullRepositoryName)
        downloadedReleasePageText = githubInteractor.getReleaseFile(self, fullRepositoryName)
        if downloadedReleasePageText:
            try:
                releasePageJSON = json.loads(downloadedReleasePageText)
                return releasePageJSON
            except:
                logging.writeError(self, "Failed to get latest release file for " + fullRepositoryName + " - skipping")
                logging.writeExecError(self, traceback.format_exc())
                return False

    # look for latest release on github
    def getReleaseAsJSON(self, repository):
        
        fullRepositoryName = githubInteractor.getFullRepositoryName(self, repository)
        if not fullRepositoryName: return False
        releasePageJSON = githubInteractor.getReleaseFileJSON(self, fullRepositoryName)
        if not releasePageJSON: return False
        return releasePageJSON

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

    # get DEB-file download URL from release file, filter for deb-packages
    def getDEBDownloadURLs(self, releaseData, packages, local_architecture_alias_list):
        try:
            assets = releaseData["assets"]
            # scheme of packagesFilenameSet: {package : {asset_name:asset_url, asset_name2:asset_url2}}
            packagesFilenameSet = {}

            for package in packages:
                packagesFilenameSet[package] = {}
                for asset in assets:
                    # try to get asset information (can be extented if required)
                    try:
                        asset_name = asset["name"]

                        for architecture_alias in local_architecture_alias_list:
                            # check if package should be synced
                            # sync packages, that have a .deb ending, arent .torrent-files, and have the correct/wanted architecture
                            if ".deb" in asset_name and package in asset_name and architecture_alias in asset_name and not ".torrent" in asset_name:
                                # link package name from config with complete package name
                                packagesFilenameSet[package][asset_name] = asset["browser_download_url"]
                                logging.writeDebug(self, "Added '" + asset_name + "' with '" + asset["browser_download_url"] + "' as URL to download set")
                    except:
                        logging.writeExecError(self, traceback.print_exc())
            return packagesFilenameSet
        except:
            logging.writeExecError(self, traceback.format_exc())
            return False, False


    # download latest release files
    def downloadHandler(self, repository, releaseData, version, oldversion):

        # get packages
        packages = configInteractor.getPackages(self, repository)
        if packages:
            logging.writeDebug(self, "Got packages " + repository + ", Packages: " + str(packages))

            # get architectures
            architectures = configInteractor.getArchitectures(self, repository)

            # check if all architectures should be downloaded -> retrieve default architectures from file
            if "all" in architectures: architectures = configInteractor.resolveAllArchitectures(self)

            # start getting files when retrieved architectures
            if architectures:
                logging.writeDebug(self, "Set architectures to sync for " + repository + ": " + str(architectures))

                # paste all architecture aliases to one list
                local_architecture_alias_list = []
                for architecture in architectures:
                    for alias in architecture_alias_list[architecture]:
                        if architecture in architectures:
                            local_architecture_alias_list.append(alias)
                    if architecture in architectures:
                        local_architecture_alias_list.append(architecture)

                logging.writeDebug(self, "Local architecture alias list for " + repository + " is " + str(local_architecture_alias_list))

                # get package URLs to download
                packagesFilenameSet = githubInteractor.getDEBDownloadURLs(self, releaseData, packages, local_architecture_alias_list)
                logging.writeDebug(self, "Package collection to download: " + str(packagesFilenameSet))

                if  packagesFilenameSet:
                    # scheme of fileToDownload is {package : {asset_name:asset_url, asset_name2:asset_url2}}
                    filesToDownload = {}

                    # iterate through to files to download and compare with architectures to download
                    for package in packagesFilenameSet.keys():
                        filesToDownload[package] = {}
                        logging.writeDebug(self, "Checking " + package)
                        for file in packagesFilenameSet[package].keys():
                            architecture_found = False
                            for architecture_alias in local_architecture_alias_list:
                                if architecture_alias in file:
                                    filesToDownload[package][file] = packagesFilenameSet[package][file]
                                    logging.writeDebug(self, "Added " + file + " to download list")
                                    architecture_found = True
                                    break
                            
                            if not architecture_found:
                                logging.writeDebug(self, "Adding " + file + " didn't found any architecture in filename") 
                                filesToDownload[package][file] = packagesFilenameSet[package][file]

                    logging.writeDebug(self, "Fileset to download: " + str(filesToDownload))

                    for package in packagesFilenameSet.keys():

                        downloadFailed = []
                        # indicator wheter anything has been downloaded (to prevent update of version although nothing was downloaded)
                        downloadedAnything = False

                        # downloads files to download directory
                        for file in packagesFilenameSet[package].keys():
                            try: 
                                wget.download(packagesFilenameSet[package][file], self.downloads + file)
                                # print empty line 
                                print()
                                logging.write(self, "Downloaded " + file + " successfully")
                            except:
                                logging.writeError(self, "Failed to download " + file)
                                logging.writeExecError(self, traceback.format_exc())
                                # add filename to list, to remove it later from the set
                                downloadFailed.append(file)
                                return 
                            downloadedAnything = True

                        try: 
                            if downloadedAnything: configInteractor.updateVersion(self, repository, version, oldversion)
                        except: 
                            logging.writeError(self, "Could not update version in config file")
                            logging.writeExecError(self, traceback.format_exc())
                    
                        for file in downloadFailed:
                            packagesFilenameSet[package].pop(file)

                        logging.writeDebug(self, "Successfully downloaded Fileset: " + str(packagesFilenameSet))
                        
                else:
                    logging.writeError(self, "There are no files to download for " + repository)
                    logging.writeDebug(self, "Failed to get download URLs")
                

            else:
                logging.writeError(self, "Failed to get architectures for " + repository)

        return packagesFilenameSet