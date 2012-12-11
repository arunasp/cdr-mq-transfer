#!/bin/sh
easy_install -U pip django djang-addons django-celery
RANDPASSW=`</dev/urandom tr -dc A-Za-z0-9| (head -c $1 > /dev/null 2>&1 || head -c 50)`
sed -i "s/^SECRET_KEY.*/SECRET_KEY = \'$RANDPASSW\'/g" settings.py
python magage.py syncdb
python magage.py migrate
