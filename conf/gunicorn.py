workers = 2
bind = 'unix:/tmp/flasksites.sock'
proc_name = 'flasksites'
pidfile = '/tmp/flasksites.pid'
errorlog = '/home/www/flask-sites-conf/gunicorn_error.log'
