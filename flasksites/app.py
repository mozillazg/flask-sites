#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import closing

import sqlite3
from flask import Flask
from flask import request
from flask import session
from flask import g
from flask import redirect
from flask import url_for
from flask import abort
from flask import render_template
from flask import flash

DATABASE = 'flasksites.db'
DEBUG = True
SECRET_KEY = '\xd5\xbdx\x0fw\x02\x0cb\x0f\xc8H\xf7QDm\xa9\xa8\x9a=r'
USERNAME = 'admin'
PASSWORD = 'admin'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect('/')
    return render_template('login.html', error=error)


@app.route('/add', methods=['GET', 'POST'])
def add_site():
    if not session.get('logged_in'):
        abort(401)

    error = None
    if request.method == 'POST':
        title = request.form.get('title', '')
        url = request.form.get('url', '')
        description = request.form.get('description', '')
        source_url = request.form.get('source_url', '')

        g.db.execute('insert into site (title, url, description, '
                     'source_url) values (?, ?, ?, ?)',
                    [title, url, description, source_url])
        g.db.commit()
        flash('New site was successfully added')
        return redirect(url_for('show_sites'))
    else:
        return render_template('add_site.html', error=None)


@app.route('/')
def show_sites():
    cur = g.db.execute('select title, url, description, source_url from '
                       'site order by id desc')
    sites = [dict(title=row[0], url=row[1], description=row[2],
               source_url=row[3]) for row in cur.fetchall()]
    return render_template('show_sites.html', sites=sites)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_sites'))

if __name__ == '__main__':
    app.run()
