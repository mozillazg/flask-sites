#!/usr/bin/env python
# -*- coding: utf-8 -*-

from settings import db


def init_db():
    db.create_all()
