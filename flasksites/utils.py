#!/usr/bin/env python
# -*- coding: utf-8 -*-

from settings import db
from models import Tag


def init_db():
    db.create_all()


def get_or_create_tag(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first()
    if tag is None:
        tag = Tag(name=tag_name)
        db.session.add(tag)
        db.session.commit()
    return tag
