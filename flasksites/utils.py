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


def thumbnail_filter(url, width=1024, height=768, selector='body'):
    api = 'http://screamshot-demo.3sd.me/capture/?url=%s'
    api += '&width=%s&height=%s&selector=%s'
    return api % (url, width, height, selector)


def shorter_url_filter(url):
    url = url.strip('http://').strip('https://')
    return url


def format_datetime_filter(value, format='%b %d, %Y'):
    return value.strftime(format)
