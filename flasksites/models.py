#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import random
import hashlib

from settings import db

__all__ = ['User', 'Site', 'Tag']


class User(db.Model):
    """base on june project(https://github.com/pythoncn/june)
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    nick_name = db.Column(db.String(80))

    # for user: 1 - not verified, 2 - verified, > 20 staff > 40 admin
    role = db.Column(db.Integer, default=1)

    is_admin = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sites = db.relationship('Site', backref='submitted_by', lazy='dynamic')

    def __init__(self, **kwargs):
        self.token = self.create_token(16)

        if 'password' in kwargs:
            raw = kwargs.pop('password')
            self.password = self.create_password(raw)

        if 'username' in kwargs:
            username = kwargs.pop('username')
            self.username = username.lower()

        if 'email' in kwargs:
            email = kwargs.pop('email')
            self.email = email.lower()

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return self.nick_name or self.username

    def __repr__(self):
        return '<Account: %s>' % self.username

    @staticmethod
    def create_password(raw):
        salt = User.create_token(8)
        passwd = '%s%s%s' % (salt, raw,
                             db.app.config['PASSWORD_SECRET'])
        hsh = hashlib.sha1(passwd).hexdigest()
        return "%s$%s" % (salt, hsh)

    @staticmethod
    def create_token(length=16):
        chars = ('0123456789'
                 'abcdefghijklmnopqrstuvwxyz'
                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        salt = ''.join([random.choice(chars) for i in range(length)])
        return salt

    def check_password(self, raw):
        if not self.password:
            return False
        if '$' not in self.password:
            return False
        salt, hsh = self.password.split('$')
        passwd = '%s%s%s' % (salt, raw, db.app.config['PASSWORD_SECRET'])
        verify = hashlib.sha1(passwd).hexdigest()
        return verify == hsh

    def get_id(self):
        return unicode(self.id)

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True


tags = db.Table(
    'tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('site_id', db.Integer, db.ForeignKey('site.id'))
)


class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    website = db.Column(db.String(260), unique=True, nullable=False)
    description = db.Column(db.Text)
    language = db.Column(db.String(50), default='English')
    tags = db.relationship('Tag', secondary=tags, backref=db.backref('sites',
                           lazy='dynamic'))
    source_url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    # slug = db.Column(db.String(260), unique=True, nullable=False)

    def __repr__(self):
        return '<site %r>' % self.website


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return '<Tag %r>' % self.name
