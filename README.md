# repdeb-helferling
Little helper software for self-hosted debian-based repositories.

## Features:
* [repdeb-sync](#repdep-sync)
* [repdeb-autoindex](#repdeb-autoindex)
* [Coming soon](#coming-soon)
* [Updating](#updating)
* [Known bugs](#known-bugs)

## repdep-sync 

Script to sync/source Debian packages automatically from Github releases

### Installation
Install the required packages:
```
$ apt install python3-pip
```
```
$ pip3 install wget
```
Create required directories
```
$ mkdir /var/log/repdeb-helferling/
```
Create this directory in the directory where the main python file is located:
```
$ mkdir downloads/
```

Add a crontab to automate sourcing:
```
$ nano /etc/cron.d/repo-helper
```
With the following content:
```
# crontab to automatically source packages from github and provide them to repository 

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name command to be executed
5 0  *  *  *  * root /usr/bin/python3 /root/repdeb-helferling/repdeb-sync.py
```
**Remember to add the correct path to the basedir in line 32 of repdeb-sync.py! Otherwise the program will not find it's config files. It MUST end with the '/'-character!**

### Configuration
Edit the config file to add repositories:

Template:
```
[<REPONAME>]
repo_name = <OWNER>/<REPONAME>
packages = <PACKAGES-TO-SYNC>
version = 
architectures = <amd64/arm64/etc.>
```
Remind to add the REPONAME to the remote_sources line in GENERAL-section!
See the provided config for more details!

Additionally remind to set the correct final directories. E.g. ```final_dir_amd64 = amd64/``` will place all binaries for ```amd64```-architectures in the directory ```<final-deb-dir>/amd64```.s

The path to the config file is defined as static variable in the header of repdeb-sync.py as variable "configFile", edit this if you're using a different directory for the config!

When adding an architecture after the script already downloaded a package for any other architecture, the added architecture will not be recognized until there is a new release. 

### How it works
```repdeb-sync``` sources the configuration file and retrieves the latest release files for each repository from GitHub. Then it starts comparing the local version of the software with the version on Github. And if there's a new release available, the script will start downloading firstly all ```.deb```-packages to a download directory. This is caused due to a lack of architecture information within the GitHub release file. After that it will clean up the download directory by checking the architecture of each package via ```dpkg --info```. Architectures that are not listet in the config file will be removed, all others will be moved to the correct repository directory. Finally ```repdep``` updates all versions in the config file.

### New since version 2.0.0
Added a debugging option via config file. To enable the debug log, edit the line ```loglevel``` and change it's value. Allowed parameters are ```1``` for usual logging and ```2```for the debug log.

Additionally ```repdeb-sync``` now cleans up the repositories directories by deleting old binaries when updating a package. If your repository contains packages that aren't synced by repdeb-sync it's required to "register" them in repdeb's index file under ```static/index.ini```. Remeber to add every single file that should be kept! Use this scheme: ```<package-name> = <file-name-1>,<file-name-2>```. E.g.
```
[...]
rustdesk=rustdesk-1.2.0-x86_64.deb,rustdesk-1.2.0-aarch64.deb
[...]
```
Spaces between the filenames can break the system.
If you ran repdeb accidentially, your files won't be deleted, repdeb always creates a backup under ```backup``` where all "old" files will be stored.

If you wish to completely disable cleanup and indexing change the ```autocleanup``` value from ```true``` to ```false```.

## repdeb-autoindex
Automatically update repositories Package and Releases files and sign them with gpg.

Content coming soon...

## Coming soon
Further development plans:
* Add auto detection of packages/repositories to sync though indexing/reading the main config file
* Installation/update script
* Automatic email notification 
* Debian-package of this project

## Updating
### How to update repdep-sync:
**For updating from 1.0 to 2.0:**

Move all config files ```.ini``` to ```.ini.bak```, then download the newer version of ```repdeb-helferling``` and afterwards update the config file to your needs, therefore that you backed up your config you can now open it and update the new config with your old values. Remind that there could be a change in structure! Be careful.

## Known bugs
* If there are two packages e.g. ```chia-blockchain``` and ```chia-blockchain-cli``` in one release, repdeb-sync will download both, although there is only ```chia-blockchain``` registered as package because it searches for the name in the release/file name. To prevent errors when moving the files only set ```chia-blockchain``` as package to sync. Repdeb will nevertheless sync both. When specifying ```chia-blockchain-cli``` as package to sync only this package will be synced because ```chia-blockchain``` does not contain ```chia-blockchain-cli```.
