#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

DEBUG = True
SECRET_KEY = r'\xd5\xbdx\x0fw\x02\x0cb\x0f\xc8H\xf7QDm\xa9\xa8\x9a=r'
PASSWORD_SECRET = r"\x8b N\xba\xe8\x86~\xc94h\xb4N\xa6'\xb9|]g\xc2\xca"

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flasksites.db'

db = SQLAlchemy(app)
