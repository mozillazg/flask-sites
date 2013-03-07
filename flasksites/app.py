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


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            error = 'confirm password'
        else:
            g.db.execute('insert into user (username, email, password) values '
                         '(?, ?, ?)', [username, email, password])
            g.db.commit()
            flash('Signup successfully')
            return redirect(url_for('login'))
    else:
        return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['email'] != 'abc@abc.com':
            error = 'Invalid email'
        elif request.form['password'] != 'abc':
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
@app.route('/sites/')
def show_sites():
    cur = g.db.execute('select id, title, url, description, source_url from '
                       'site order by id desc')
    sites = [dict(id=row[0], title=row[1], url=row[2], description=row[3],
             source_url=row[4]) for row in cur.fetchall()]
    return render_template('index.html', sites=sites)


@app.route('/sites/mine/')
def show_mine_sites():
    if not session.get('logged_in'):
        abort(401)

    cur = g.db.execute('select id, title, url, description, source_url from '
                       'site order by id desc')
    sites = [dict(id=row[0], title=row[1], url=row[2], description=row[3],
             source_url=row[4]) for row in cur.fetchall()]
    return render_template('show_sites.html', sites=sites)


@app.route('/sites/search/')
def search_sites():
    keyword = request.args.get('q')
    if not keyword:
        return redirect('/')
    cur = g.db.execute('select id, title, url, description, source_url from '
                       'site where title like "%?%" or description like '
                       '"%?%" order by id desc', [keyword, keyword])
    sites = [dict(id=row[0], title=row[1], url=row[2], description=row[3],
             source_url=row[4]) for row in cur.fetchall()]
    return render_template('show_sites.html', sites=sites, keyword=keyword)


@app.route('/site/<int:site_id>')
def show_site(site_id):
    cur = g.db.execute('select title, url, description, source_url from '
                       'site where id=?', [site_id])
    site = [dict(title=row[0], url=row[1], description=row[2],
            source_url=row[3]) for row in cur.fetchall()]
    if site:
        site = site[0]
    return render_template('site.html', site=site)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_sites'))

if __name__ == '__main__':
    app.run()
