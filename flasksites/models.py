#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from settings import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sites = db.relationship('Site', backref='submitted_by', lazy='dynamic')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

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
