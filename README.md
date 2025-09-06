# create-issue

A command line tool to create gitlab issues and optionally create a linked merge request

## About

I often find myself needing to add a fix or improvement to my code while I'm working on it. I like to keep my
merge requests clean and try to address one problem/improvement only (I don't always succeed, but I'm learning).
To help this workflow I create issues and merge requests for every step I'm working on. Opening the gitlab web ui,
finding the issue page and creating an issue with a merge request attached kind of breaks my focus and to avoid that
I created this little tool. It allows me to create an issue and merge request in one command!

This tool will detect the gitlab url and project from the git information of the project you're currently in (so it 
won't work if your current directory is outside of a git project).

## Usage

```
usage: create-issue [-h] [--version] -t TITLE [-d DESCRIPTION] [-a ASSIGNEE]
                    [-r REVIEWER] [--type {incident,task,issue}] [-l LABEL]
                    [-m]

Create GitLab issue (and optionally MR)

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -t, --title TITLE     Title of the issue
  -d, --description DESCRIPTION
                        Description of the issue
  -a, --assignee ASSIGNEE
                        Username to assign the issue
  -r, --reviewer REVIEWER
                        Username to add as MR reviewer
  --type {incident,task,issue}
                        Type of issue
  -l, --label LABEL     Label to add to the issue
  -m, --mr              Also create a merge request
```

## Install

To install you'll need pipx (`apt install pipx` on debian/ubuntu).

Clone this repo to your local machine, then

```
#> cd create-issue
#> pipx install .
```

It will install in `~/.local/bin/` so you'll need to make sure to add this to your `PATH`

## Upgrade

To upgrade, from the cloned repo directory run the following

```
#> git pull
#> pipx upgrade create-issue
```
