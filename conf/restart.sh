#!/bin/sh

cd ../flask-sites/

git pull

pip install -r requirements.txt

cd ../flask-sites-conf/


chown www-data:www-data /home/www -R



./stop.sh
./start.sh
