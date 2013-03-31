#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import urllib
from markdown2 import markdown

from flask import url_for

from settings import db
from models import Tag
from models import User


def init_db():
    db.create_all()


def get_or_create_tag(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first()
    if tag is None:
        tag = Tag(name=tag_name)
        db.session.add(tag)
        db.session.commit()
    return tag


# def thumbnail_filter(url, width=1024, height=768, selector='body'):
    # api = 'http://screamshot-demo.3sd.me/capture/?url=%s'
    # api += '&width=%s&height=%s&selector=%s'
    # return api % (url, width, height, selector)
def thumbnail_filter(url, size='full', format='png'):
    parameters = urllib.urlencode({'url': url, 'type': format})
    api = 'http://api.snapito.com/web/abc123/%s?%s'
    return api % (size, parameters)


def shorter_url_filter(url):
    return pretty_url(re.sub(r'^https?://', '', url))


def pretty_url(url):
    return re.sub(r'(^https?://[^/\.]+\.[a-zA-Z]+)/$', r'\1', url)


def format_datetime_filter(value, format='%b %d, %Y'):
    return value.strftime(format)


def markdown_filter(text, safe_mode=None):
    if safe_mode == 'safe' or safe_mode == 'replace':
        safe_mode = 'replace'  # True
    elif safe_mode:
        safe_mode = 'escape'
    return markdown(text, safe_mode=safe_mode)


def current_link_filter(request, view_name, class_name='active', **values):
    if request.path == url_for(view_name, **values):
        return class_name
    else:
        return ''


def create_user(username, email, password):
    user = User(username=username.lower(),
                email=email.lower(), password=password)
    db.session.add(user)
    db.session.commit()
    return user


def set_password(user, password):
    user.password = User.create_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def auth_user(email, password):
    user = User.query.filter_by(email=email.lower()).first()
    if user is None:
        return None
    else:
        return user if user.check_password(password) else None
