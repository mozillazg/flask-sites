#!/bin/sh

gunicorn_conf="`pwd`/gunicorn.py"

cd /home/www/flask-sites/flasksites/


pwd

#gunicorn app:app -c $gunicorn_conf -D
gunicorn app:app -c "/home/www/flask-sites-conf/gunicorn.py" -D
