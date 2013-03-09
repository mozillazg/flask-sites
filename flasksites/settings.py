#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

DEBUG = True
SECRET_KEY = '\xd5\xbdx\x0fw\x02\x0cb\x0f\xc8H\xf7QDm\xa9\xa8\x9a=r'

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flasksites.db'

db = SQLAlchemy(app)
