# repdeb-helferling
Little helper for debian-based repositories.

## Features:
* [repdeb-sync](#repdep-sync)
* [repdeb-autoindex](#repdeb-autoindex)

## repdep-sync 

Script to sync/source Debian packages automatically from Github releases

Install the required packages:
```
$ apt install python3-pip
```
```
$ pip3 install wget
```
Create required directories
```
$ mkdir /var/log/repo-helper/
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
5 0  *  *  *  * root /usr/bin/python3 /root/repo-helper/sync-repo-from-github.py
```
Remember to add the correct path to your config file in line 29/30, otherwise the autorun cannot run correctly...


Edit the config file to add repositories:

Template:
```
[<REPONAME>]
repo_name = <OWNER>/<REPONAME>
packages = <PACKAGES-TO-SYNC>
version = 
architectures = <amd64/arm64/etc.>
name_scheme_arm64 = 
name_scheme_amd64 = ?PACKAGE?-?VERSION?.deb
name_scheme_armhf = 
```
Remind to add the REPONAME to the remote_sources line in GENERAL-section!
See the provided config for more details!

## repdeb-autoindex
Automatically update repositories Package and Releases files and sign them with gpg.

Content coming soon...
