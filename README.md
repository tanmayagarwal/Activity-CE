Activity-CE [![Build Status](https://travis-ci.org/toladata/TolaActivity.svg?branch=master)]
====
Activity-CE is the community edition of TolaActivity; the ultimate tool for humanitarians to manage project activities for their programs, including project approval workflows and reporting. 


The community edition is for and by humanitarians; it shall always be free.

## To deploy locally via virtualenv
(Install virtualenv)
```bash
$ pip install virtualenv
```
(Create Virtualenv)
```bash
$ virtualenv --no-site-packages venv
```
* use no site packages to prevent virtualenv from using your global packages

(Activate Virtualenv)
```bash
$ source venv/bin/activate
```
## Install Requirements
```bash
$ pip install -r requirements.txt
```

## Modify the config file

```yaml
47 DATABASES:
48  'default': {
49    #'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
50    'ENGINE': "django.db.backends.mysql"
51    'NAME': ""
52    'USER': ""
53    'PASSWORD': '',
54    'HOST': ""
55    'PORT': '',
```
* Replace user and password by your Mysql username and password 

## Set up Database
```bash
$ python manage.py migrate
```
* If you get access denied, it means you need to modify the config file and write your Mysql username and password in the file

# Run Activity-CE
If your using more then one settings file change manage.py to point to local or dev file first
```bash
$ python manage.py runserver
```

